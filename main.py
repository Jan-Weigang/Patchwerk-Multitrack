import os
import re
from flask import Flask, render_template, request, url_for
import random



def parse_music_files(base_directory):
    genres = {}
    # Traverse through each genre directory
    for genre in os.listdir(base_directory):
        genre_path = os.path.join(base_directory, genre)
        if os.path.isdir(genre_path):  # Ensure it's a directory
            if debug:
                print(f"Parsing genre: {genre}")
            genres[genre] = {}
            for filename in os.listdir(genre_path):
                if filename.endswith('.mp3'):
                    nickname, instrument = filename.rsplit('_', 1)
                    instrument = instrument.replace('.mp3', '')
                    if nickname not in genres[genre]:
                        genres[genre][nickname] = {'instruments': [], 'instrument_count': 0}
                    genres[genre][nickname]['instruments'].append(instrument)
                    genres[genre][nickname]['instrument_count'] += 1  # Increment the count of instruments

                    # Attempt to find and parse the associated txt file
                    txt_file_path = os.path.join(genre_path, nickname + '.txt')
                    if os.path.isfile(txt_file_path):
                        with open(txt_file_path, 'r') as file:
                            metadata = file.read().splitlines()
                            genres[genre][nickname]['metadata'] = parse_metadata(metadata)
                else:
                    continue
    return genres

def sort_music_files(music_files):
    sorted_music_files = {}
    for genre in sorted(music_files.keys()):
        tracks = music_files[genre]
        # Create a sorted list of tracks based on 'instrument_count'
        sorted_tracks = sorted(tracks.items(), key=lambda item: item[1]['instrument_count'], reverse=False)
        # Convert the list of tuples back to a dictionary
        sorted_music_files[genre] = {nickname: details for nickname, details in sorted_tracks}
    return sorted_music_files



# def parse_metadata(lines):
#     metadata_dict = {}
#     for line in lines:
#         if ':' in line:
#             key, value = line.split(':', 1)
#             metadata_dict[key.strip()] = value.strip()
#     return metadata_dict

def parse_metadata(lines):
    metadata_dict = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)  # Split on the first colon
            metadata_dict[key.strip()] = value.strip()  # Remove any extra whitespace
    return metadata_dict



def file_exists(full_path):
    return os.path.isfile(full_path)

def normalize_instrument_name(name):
    return re.sub(r'\d+$', '', name)

def sort_instruments(instruments):
    instrument_order = app.config['INSTRUMENT_ORDER']
    sorted_instruments = sorted(instruments, key=lambda x: instrument_order.index(normalize_instrument_name(x)) if normalize_instrument_name(x) in instrument_order else len(instrument_order))
    return sorted_instruments



def image_exists(instrument):
    # Remove all digits from the instrument name and append '.jpg'
    clean_instrument_name = normalize_instrument_name(instrument)
    image_filename = f"{clean_instrument_name}.jpg"
    image_path = os.path.join(instrument_directory, image_filename)
    
    if file_exists(image_path):
        return image_filename

    print(f"No Image for {instrument}")
    return None


def is_too_similar(instrument, existing_instruments):
    # Check for specific substrings that should not coexist
    keyword_groups = {
        'drum': ['drum', 'drums', 'drumset', 'e-drums', 'hihat', 'claps', 'snaredrum', 'kickdrum'],
        'synth': ['synth', 'synthesizer', 'synthbass', 'melodiesynth', 'backgroundsynth'],
        'string': ['violin', 'cello', 'bass', 'guitar', 'harp'],
        'fx': ['hall', 'effekte']
        # Add other groups as needed
    }

    # Convert all to lower_case
    instrument= instrument.lower()
    existing_instruments = [existing.lower() for existing in existing_instruments]

    # Filter already existing instruments
    for existing in existing_instruments:
        if instrument in existing or existing in instrument:
            return True
        
    # Filter instruments that are similar by keyword
    for keywords in keyword_groups.values():
        if any(keyword in instrument for keyword in keywords):
            if any(any(keyword in existing for keyword in keywords) for existing in existing_instruments):
                if debug:
                    print(f"I just FILTERED OUT {instrument} vs {existing_instruments}")
                return True

    # Filter instruments with digits
    if re.search(r'\d+$', instrument):
        return True

    if debug:
        print(f"I just checked {instrument} vs {existing_instruments} and it is not too similar")
    return False

def add_random_instruments(original_instruments: list, amount: int):
    # # Get a flat list of all possible instruments, excluding those too similar to existing ones
    # all_possible_instruments = [
    #     instr for subdict in music_files.values()
    #     for nick in subdict.values()
    #     for instr in nick.get('instruments', [])
    #     if not is_too_similar(instr, original_instruments)
    # ]

    # First, gather all possible instruments into a list without filtering
    all_possible_instruments = [
        instr for subdict in music_files.values()
        for nick in subdict.values()
        for instr in nick.get('instruments', [])
    ]

    # Convert list to set to remove duplicates
    unique_possible_instruments = set(all_possible_instruments)

    # Filter out instruments that are too similar to the original ones
    filtered_possible_instruments = [
        instr for instr in unique_possible_instruments
        if not is_too_similar(instr, original_instruments)
    ]

    # Randomly pick 4 additional instruments that are not too similar
    random_instruments = random.sample(filtered_possible_instruments, min(amount, len(filtered_possible_instruments)))
    if debug:
        print(f"picked random instruments: {random_instruments} from max of {len(filtered_possible_instruments)}")

    # Combine and sort instruments
    combined_instruments = list(set(original_instruments + random_instruments))
    sorted_instruments = sort_instruments(combined_instruments)
    return sorted_instruments



def get_instrument_data(instruments, original_instruments=[]):
    instrument_data = {
        instr: {
            'image': image_exists(f"{instr}"),
            'original': instr in original_instruments,
            'fx': instr in app.config['FX']  # Set 'fx' to true if instrument is in the special set
        }
        for instr in instruments
    }
    return instrument_data






app = Flask(__name__)
debug = False
# Define the preferred order of instruments
app.config['INSTRUMENT_ORDER'] = ['Vocals', 'VintageVocals', 'BackingVocals', 'Wispern', 'Hall',
                                  'Trompete', 'Trompeten', 'Saxofone', 'Saxofon', 'Posaunen', 'Posaune', 'Bläsersatz', 'Blechbläser', 
                                  'Klarinette', 'Klarinetten', 'Holzbläser', 
                                  'Streicher', 'Violinen', 'Violine', 'Bratschen', 'Bratsche', 'Celli', 'Cello', 'Kontrabass', 'Kontrabässe',
                                  'MelodieSynth', 'Solo-E-Gitarre', 
                                  'MelodieSchlagwerk', 'Schlagwerk',
                                  'Piano', 'StagePiano', 'Rhodes', 'HammondOrgel', 'Keyboard', 'Synth', 'BackgroundSynth', 
                                  'E-Gitarre', 'Gitarren-Amp', 'Gitarre', 'E-Bass', 'Bass-Amp', 'SynthBass', 'Jazz-Kontrabass', 
                                  'Percussion', 'Cabasa', 'Maracas', 
                                  'E-Drums', 'Drumset', 'Drums', 'VintageDrums', 
                                  'HiHat', 'Claps', 'SnareDrum', 'KickDrum', 
                                  'Hall-Effekt', 'Effekte']
app.config['FX'] = ['Gitarren-Amp', 'Bass-Amp', 'Hall']

base_dir = os.path.abspath(os.path.dirname(__file__))
music_directory = os.path.join(base_dir, 'static', 'music')
instrument_directory = os.path.join(base_dir, 'static', 'instruments')
effects_directory = os.path.join(base_dir, 'static', 'effects')
music_files = sort_music_files(parse_music_files(music_directory))

if debug:
    print(f"music files is: {music_files}")
    print(f"- - - - - - -")
    print(f"- - - - - - -")
print("files loaded")


@app.route('/')
def index():
    return render_template('index.html', music_files=music_files)


@app.route('/play/', defaults={'genre': None, 'nickname': None})
@app.route('/play/<genre>/<nickname>')
def play(genre, nickname):

    if genre is None:
        genre = random.choice(list(music_files.keys()))
    genre_info = music_files.get(genre, {})
    if nickname is None:
        nickname = random.choice(list(genre_info.keys()))
    track_info = genre_info.get(nickname, {})
        
    instruments = track_info.get('instruments', [])

    # Get Data Ready for Template
    sorted_instruments = sort_instruments(instruments)
    instrument_data = get_instrument_data(sorted_instruments)
    metadata=track_info.get('metadata', {})

    return render_template('play.html', nickname=nickname, genre=genre, instruments=instrument_data, metadata=metadata, music_directory=os.path.join(music_directory, genre))


@app.route('/effects')
def effects():
    # Get Info from files.
    effects_files = os.listdir(effects_directory)
    instruments = [os.path.splitext(file)[0] for file in effects_files if file.endswith('.mp3')]

    # Get Data Ready for Template
    sorted_instruments = sort_instruments(instruments)
    instrument_data = get_instrument_data(sorted_instruments)

    return render_template('effects.html', instruments=instrument_data, music_directory=os.path.join(effects_directory))



@app.route('/full_mix_test/', defaults={'difficulty': None})
@app.route('/full_mix_test/<difficulty>')
def full_mix_test(difficulty):
    # Randomly select a genre and a track
    genre = random.choice(list(music_files.keys()))
    genre_info = music_files[genre]
    nickname = random.choice(list(genre_info.keys()))
    track_info = genre_info[nickname]

    if not difficulty == 'hard':
        difficulty = 'easy'

    print(difficulty)

    #save the orivinal instruments
    original_instruments = track_info.get('instruments', [])

    # DEBUG: print(f"Track: {track_info} and instruments: {original_instruments}")

    # Get Data Ready for Template
    sorted_instruments = add_random_instruments(original_instruments, 4)
    instrument_data = get_instrument_data(sorted_instruments, original_instruments)
    metadata = track_info.get('metadata', {})

    return render_template('test.html', difficulty=difficulty, nickname=nickname, genre=genre, instruments=instrument_data, metadata=metadata, music_directory=os.path.join(music_directory, genre))



@app.route('/instrument_test')
def instrument_test():
    # Randomly select a genre and a track
    genre = random.choice(list(music_files.keys()))
    genre_info = music_files[genre]
    nickname = random.choice(list(genre_info.keys()))
    track_info = genre_info[nickname]

    # Get the primary instrument for the selected track
    primary_instrument = random.choice(track_info.get('instruments', []))
    sorted_instruments = add_random_instruments([primary_instrument], 3)


    # Prepare instrument data
    instrument_data = get_instrument_data(sorted_instruments, primary_instrument)
    metadata = track_info.get('metadata', {})

    if  debug:
        print(f"rendering an instrument test with instruments {sorted_instruments} and data: {instrument_data}")
    return render_template('test.html', difficulty='einzel', nickname=nickname, genre=genre, instruments=instrument_data, metadata=metadata, music_directory=os.path.join(music_directory, genre))



if __name__ == '__main__':
    app.run(debug=False)