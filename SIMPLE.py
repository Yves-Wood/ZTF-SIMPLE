import os
import math
import pandas as pd
import numpy as np
from astropy.timeseries import LombScargle
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def process_csv_files_in_all_parent_dirs():
    """
    Processes CSV files in all parent directories. 
    Each parent directory represents an object, and figures are generated for each CSV. 
    This is hell.
    """
    # Get the directory of the current script
    base_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Loop through all directories and files in the base directory
    for root, dirs, files in os.walk(base_directory):
        for directory in dirs:
            parent_path = os.path.join(root, directory)  # Path to each parent directory
            
            # Create output directory inside the parent folder if it doesn't exist
            create_output_directory(parent_path)
            
            # Process each CSV file in the current parent directory
            for file in os.listdir(parent_path):
                if file.endswith(".csv") and is_valid_csv_name(file):
                    input_file = os.path.join(parent_path, file)
                    
                    # Call the function to generate figures for the current CSV file
                    plot_combined_figures(input_file, min_per, max_per, error_enable, grid_enable, parent_path)

def create_output_directory(output_file):
    """Creates a directory with the name of the output file if it doesn't exist."""
    if not os.path.exists(output_file):
        os.makedirs(output_file)

def is_valid_csv_name(filename):
    """Checks if the CSV file name matches 'processed_ZTF_{band}'."""
    valid_bands = ['i', 'g', 'r']
    for band in valid_bands:
        if filename == f'processed_ZTF_{band}.csv':
            return True
    return False

def plot_combined_figures(input_file, min_per, max_per, error_enable, grid_enable, parent_path):
    print(f'Generating combined figure for {input_file}...')


    # Creates the base name
    base_name = os.path.splitext(input_file)[0]
    band_name = os.path.basename(base_name)
    object_name = os.path.basename(parent_path)

    if band_name == 'processed_ZTF_i':
        band_name = 'zi'
    elif band_name == 'processed_ZTF_r':
        band_name = 'zr'
    else:
        band_name = 'zg'



    # Sets the font
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 15

    # Create a figure with 3 subplots (3 rows, 1 column)
    fig, axs = plt.subplots(3, 1, figsize=(11, 15))  # Adjust figure size as needed

    fig.suptitle(f"{band_name} analysis of {object_name}")

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Filter out rows where catflags > 0
    df_filtered = df[df['catflags'] == 0]

    # Extract data for scatter plot
    x_data = df_filtered["mjd"]
    y_data = df_filtered["mag"]
    mag_err = df_filtered["magerr"]

    # Plot scatter plot in the first subplot
    axs[0].scatter(x_data, y_data, color='cornflowerblue')
    if error_enable:
        axs[0].errorbar(x_data, y_data, yerr=mag_err, fmt='none', ecolor='cornflowerblue', capsize=5, label='Y-Errors')
    axs[0].invert_yaxis()
    axs[0].set_xlabel("mjd")
    axs[0].set_ylabel(f"{band_name} (mag)")
    axs[0].set_title('')
    if grid_enable:
        axs[0].grid(True)
    else:
        axs[0].grid(False)

    #Sets amount of Y- axis ticks
    axs[0].yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))

    # Perform Lomb-Scargle periodogram analysis using filtered data
    time = df_filtered["mjd"].values
    flux = df_filtered["mag"].values
    frequency, power = LombScargle(time, flux).autopower()

    # Find the index of the maximum power
    max_power_index = np.argmax(power)

    # Retrieve the corresponding frequency
    max_power_frequency = frequency[max_power_index]

    # Calculate the period (inverse of frequency)
    max_power_period = 1 / max_power_frequency

    # Plot periodogram in the second subplot
    axs[1].plot(1 / frequency, power, color='cornflowerblue')
    if min_per is not None and max_per is not None:
        axs[1].set_xlim(min_per, max_per)
    axs[1].set_ylim(bottom=0)
    axs[1].set_xlabel('Period (days)')
    axs[1].set_ylabel('Power')
    axs[1].set_xscale('log')
    axs[1].yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))

    # Calculate phase for the phase-folded graph using filtered data
    phase = (time / max_power_period) % 1
    sorted_indices = np.argsort(phase)
    phase_sorted = phase[sorted_indices]
    flux_sorted = flux[sorted_indices]
    magerr_sorted = mag_err.values[sorted_indices]  # Ensure mag_err matches filtered and sorted indices

    # Extend the phase-folded graph to a phase of 2
    phase_extended = np.concatenate([phase_sorted, phase_sorted + 1])
    flux_extended = np.concatenate([flux_sorted, flux_sorted])
    mag_err_extended = np.concatenate([magerr_sorted, magerr_sorted])

    rounded_period = round(max_power_period, 3)

    # Plot phase-folded graph in the third subplot
    axs[2].scatter(phase_extended, flux_extended, color='cornflowerblue')
    if error_enable:
        axs[2].errorbar(phase_extended, flux_extended, yerr=mag_err_extended, fmt='none', ecolor='cornflowerblue', capsize=5, label='Y-Errors')
    axs[2].set_xlim(0, 2)
    axs[2].set_xlabel('Phase')
    axs[2].set_ylabel(f'{band_name} (mag)')
    axs[2].set_title(f'Period = {rounded_period} days')
    axs[2].invert_yaxis()
    axs[2].yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))

    # Adjust layout and save the combined figure
    plt.tight_layout()
    output_file = os.path.join(os.path.dirname(input_file), f"{base_name}_combined_figure.png")
    plt.savefig(output_file)

    #Creates a .txt file that saves results
    text_output_file = os.path.join(parent_path, f"{object_name}_{band_name}_analysis.txt")
    with open(text_output_file, 'a') as f:
        f.write(f"Object: {object_name}\n")
        f.write(f"Spreadsheet: {band_name}\n")
        f.write(f"Power: {round(power[max_power_index], 3)}\n")
        f.write(f"Period (d): {rounded_period}\n")
        f.write("\n")  # Add a new line to separate entries
    
    print(f"Analysis results saved to {text_output_file}")

def process_csv_files():
    # Processes CSV files in all parent directories. Each parent directory represents an object, and figures are generated for each CSV
    
    base_directory = os.path.dirname(os.path.abspath(__file__))

    for root, dirs, files in os.walk(base_directory):
        for directory in dirs:
            parent_path = os.path.join(root, directory)

            create_output_directory(parent_path)

            for file in os.listdir(parent_path):
                if file.endswith(".csv"):
                    input_file = os.path.join(parent_path, file)
                    process_and_split_csv(input_file, parent_path)

def create_output_directory(output_file):
    if not os.path.exists(output_file):
        os.makedirs(output_file)

def process_and_split_csv(input_file, parent_path):
    try:
        # Try loading the CSV file with UTF-8 encoding first
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f'Processing {input_file}...')

        # Check for the existence of critical columns
        required_columns = ['infobitssci', 'filter', 'zpdiff', 'nearestrefmag', 
                            'forcediffimflux', 'forcediffimfluxunc', 'jd', 'procstatus']
        for col in required_columns:
            if col not in df.columns:
                print(f"Column '{col}' not found in {input_file}. Skipping this file.")
                return

        # Filter based on 'infobitssci' and reset index
        df_filtered = df[df['infobitssci'] < 33554432].reset_index(drop=True)

        if df_filtered.empty:
            print(f"{input_file} has no valid data after filtering.")
            return

        # Additional check for null values in critical columns
        df_filtered.dropna(subset=['zpdiff', 'nearestrefmag', 'forcediffimflux', 'forcediffimfluxunc', 'jd', 'procstatus'], inplace=True)

        if df_filtered.empty:
            print(f"{input_file} has no valid data after removing rows with null values.")
            return

        # Handle 'filter' types and process accordingly
        filters = ['ZTF_g', 'ZTF_r', 'ZTF_i']

        for filter_type in filters:
            df_filter_specific = df_filtered[df_filtered['filter'] == filter_type]

            if df_filter_specific.empty:
                print(f"No data for filter '{filter_type}' in {input_file}.")
                continue

            results = compute_photometry(df_filter_specific)

            if results:
                output_file = os.path.join(parent_path, f"processed_{filter_type}.csv")
                df_results = pd.DataFrame(results, columns=['mag', 'magerr', 'mjd'])
                df_results['catflags'] = 0  # Add catflags column with a default value
                df_results.to_csv(output_file, index=False)
                print(f"Output saved to {output_file}.")
            else:
                print(f"No valid photometry results for filter '{filter_type}' in {input_file}.")

    except pd.errors.EmptyDataError:
        print(f"{input_file} is empty or has no data. Skipping.")
    except pd.errors.ParserError:
        print(f"Error parsing {input_file}. There might be issues with file format or encoding.")
    except Exception as e:
        print(f"Error processing {input_file}: {e}")

def compute_photometry(df_filtered):
    results = []

    if df_filtered.empty:
        return results

    zpdiff = df_filtered['zpdiff']
    nearestrefmag = df_filtered['nearestrefmag']
    forcediffimflux = df_filtered['forcediffimflux']
    forcediffimfluxunc = df_filtered['forcediffimfluxunc']
    jd = df_filtered['jd']
    procstatus = df_filtered['procstatus']

    SNT = 3  # Signal-to-noise threshold
    SNU = 5  # Signal-to-noise upper bound for error cases

    nearestrefflux = 10 ** (0.4 * (zpdiff - nearestrefmag))
    nearestreffluxunc = df_filtered['nearestrefmagunc'] * nearestrefflux / 1.0857
    flux_tot = forcediffimflux + nearestrefflux
    fluxunc_tot = (forcediffimfluxunc ** 2 + nearestreffluxunc ** 2) ** 0.5
    snr_tot = flux_tot / fluxunc_tot

    for idx, row in df_filtered.iterrows():
        try:
            if snr_tot[idx] > SNT and procstatus[idx] == 0:
                flux_tot_log = math.log10(flux_tot[idx])
                mag = zpdiff[idx] - 2.5 * flux_tot_log
                magerr = 1.0857 / snr_tot[idx]
                mjd = jd[idx] - 2400000.5
            elif procstatus[idx] == 0 and snr_tot[idx] <= SNT:
                compute_log = math.log10(SNU * fluxunc_tot[idx])
                mag = zpdiff[idx] - 2.5 * compute_log
                magerr = None
                mjd = jd[idx] - 2400000.5
            else:
                continue

            results.append([mag, magerr, mjd])

        except (ValueError, KeyError, IndexError) as e:
            print(f"Error computing photometry for row {idx}: {e}")

    return results

def txt_to_csv(file_name):
    # Read the txt file
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # Remove the first 56 rows and the 58th row (which is now at index 2) and the last row (index -1)
    cleaned_lines = lines[55:]  # Start from the 57th row (index 56)

    if len(cleaned_lines) > 1:  # Ensure there are enough lines
        cleaned_lines.pop(1)  # Remove the blank row

    if len(cleaned_lines) > 1:
        cleaned_lines.pop(1)  # Remove the duplicate row

    if len(cleaned_lines) > 1:
        cleaned_lines.pop(-1)  # Remove the last row

    # Process lines (split by spaces, tabs, or whatever delimiter your file uses)
    data = [line.strip().split() for line in cleaned_lines]

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Remove any trailing commas from column names (if present)
    df.columns = df.iloc[0].str.rstrip(',')  # Assume the first row is the header
    df = df[1:]  # Drop the header row from the data

    # Sort the DataFrame by the 'filter' column if it exists
    if 'filter' in df.columns:
        df = df.sort_values(by='filter', key=lambda col: col.map({'ZTF_g': 0, 'ZTF_r': 1, 'ZTF_i': 2}))

    # Create a directory with the name of the input file (without .txt extension)
    folder_name = file_name.replace('.txt', '')
    os.makedirs(folder_name, exist_ok=True)  # Create the folder if it doesn't exist

    # Save to CSV in the new folder with the same name but .csv extension
    csv_file_name = os.path.join(folder_name, file_name.replace('.txt', '.csv'))
    df.to_csv(csv_file_name, index=False)
    print(f"Converted {file_name} to {csv_file_name}")

def batch_convert_txt_to_csv():
    # Get the current directory where the program is located
    current_directory = os.getcwd()

    # Iterate through all files in the current directory
    for filename in os.listdir(current_directory):
        if filename.endswith('.txt'):
            txt_to_csv(filename)

# Set default values for min_per, max_per, and error_enable
min_per = None
max_per = None
error_enable = True
grid_enable = True

batch_convert_txt_to_csv()

process_csv_files()

use_SIMPLE = input('\nWould you like to generate figures for the processed files? Y/N \n')

if use_SIMPLE.lower() == 'y':
    # Call the function to process all parent directories
    process_csv_files_in_all_parent_dirs()
else:
    quit()
