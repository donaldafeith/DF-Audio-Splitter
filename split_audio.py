import os
from spleeter.separator import Separator

def split_audio(input_file, output_directory, num_stems):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Determine the Spleeter model based on the number of stems
    model_map = {
        2: 'spleeter:2stems',
        3: 'spleeter:3stems',
        4: 'spleeter:4stems',
        5: 'spleeter:5stems'
    }
    if num_stems not in model_map:
        raise ValueError("Invalid number of stems. Please choose between 2, 3, 4, and 5.")

    # Initialize the Spleeter separator
    separator = Separator(model_map[num_stems])

    # Separate the audio file
    separator.separate_to_file(input_file, output_directory)

    # Optional: Rename the separated files for convenience
    track_name_map = {
        2: ['vocals', 'accompaniment'],
        3: ['vocals', 'drums', 'other'],
        4: ['vocals', 'drums', 'bass', 'other'],
        5: ['vocals', 'drums', 'bass', 'piano', 'other']
    }
    track_names = track_name_map[num_stems]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    for track in track_names:
        src = os.path.join(output_directory, base_name, track + '.wav')
        dst = os.path.join(output_directory, base_name + '_' + track + '.wav')
        if os.path.exists(src):
            os.rename(src, dst)
    print(f"Tracks have been saved in {output_directory}")

if __name__ == "__main__":
    input_file = input("Enter the path to your audio file: ")
    output_directory = input("Enter the path to the directory where you want to save the split tracks: ")
    num_stems = int(input("Enter the number of splits you want (choose between 2, 3, 4, and 5): "))
    split_audio(input_file, output_directory, num_stems)