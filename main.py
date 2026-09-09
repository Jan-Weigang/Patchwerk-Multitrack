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


# Neu, beachtet Familiennähe
def add_random_instruments(original_instruments: list, amount: int):
    random_instruments = pick_weighted_instrument_names(
        original_instruments, amount, exclude=original_instruments
    )
    if debug:
        print(f"gewichtet gewählt: {random_instruments}")
    combined = list(set(original_instruments + random_instruments))
    return sort_instruments(combined)

# def add_random_instruments(original_instruments: list, amount: int):
#     # # Get a flat list of all possible instruments, excluding those too similar to existing ones
#     # all_possible_instruments = [
#     #     instr for subdict in music_files.values()
#     #     for nick in subdict.values()
#     #     for instr in nick.get('instruments', [])
#     #     if not is_too_similar(instr, original_instruments)
#     # ]

#     # First, gather all possible instruments into a list without filtering
#     all_possible_instruments = [
#         instr for subdict in music_files.values()
#         for nick in subdict.values()
#         for instr in nick.get('instruments', [])
#     ]

#     # Convert list to set to remove duplicates
#     unique_possible_instruments = set(all_possible_instruments)

#     # Filter out instruments that are too similar to the original ones
#     filtered_possible_instruments = [
#         instr for instr in unique_possible_instruments
#         if not is_too_similar(instr, original_instruments)
#     ]

#     # Randomly pick 4 additional instruments that are not too similar
#     random_instruments = random.sample(filtered_possible_instruments, min(amount, len(filtered_possible_instruments)))
#     if debug:
#         print(f"picked random instruments: {random_instruments} from max of {len(filtered_possible_instruments)}")

#     # Combine and sort instruments
#     combined_instruments = list(set(original_instruments + random_instruments))
#     sorted_instruments = sort_instruments(combined_instruments)
#     return sorted_instruments



def get_instrument_data(instruments, original_instruments=None):
    if original_instruments is None:
        original_instruments = []
    elif isinstance(original_instruments, str):
        original_instruments = [original_instruments]

    instrument_data = {
        instr: {
            'image': image_exists(f"{instr}"),
            'original': instr in original_instruments,
            'fx': instr in app.config['FX']  # Set 'fx' to true if instrument is in the special set
        }
        for instr in instruments
    }
    return instrument_data

def _family_members(groups):
    return [instr for group in groups for instr in group]





app = Flask(__name__)
debug = False
# Define the preferred order of instruments
INSTRUMENT_FAMILIES = {
    'Gesang':      [['Vocals'], ['Sopran'], ['Alt'], ['Tenor'], ['Bass'],
                    ['VintageVocals'], ['BackingVocals'], ['Wispern']],
    'Holzbläser':  [['Querflöte', 'Querflöten', 'Flöten'], ['Klarinette', 'Klarinetten'],
                    ['Oboe'], ['Fagott'], ['Holzbläser'], ['Saxophon', 'Saxophone'], ['Sopransaxophon'],['Altsaxophon'], ['Tenorsaxophon'], ['Baritonsaxophon']],
    'Blechbläser': [['Trompete', 'Trompeten'], ['Posaune', 'Posaunen'], ['Horn', 'Hörner'],
                    ['Tuba'], ['Bläsersatz'], ['Blechbläser']],
    'Streicher':   [['Streicher'], ['Violine', 'Violinen'],
                    ['Viola', 'Violas', 'Bratsche', 'Bratschen'], ['Cello', 'Celli'],
                    ['Kontrabass', 'Kontrabässe'], ['Jazz-Kontrabass']],
    'Tasten':      [['Piano'], ['StagePiano'], ['Rhodes'], ['HammondOrgel'], ['Keyboard'], ['Akkordion']],
    'Synth':       [['MelodieSynth', 'Synth', 'BackgroundSynth'], ['SynthBass']],
    'Gitarre':     [['Solo-E-Gitarre', 'E-Gitarre', 'Gitarren-Amp'], ['Gitarre'], ['Banjo'], ['Mandoline']],
    'Bass':        [['E-Bass', 'Bass-Amp']],
    'Percussion':  [['MelodieSchlagwerk'], ['Schlagwerk', 'Percussion', 'Cabasa', 'Maracas', 'Shaker']],
    'Drums':       [['E-Drums', 'Drumset', 'Drums', 'VintageDrums'],
                    ['HiHat'], ['Claps'], ['SnareDrum'], ['KickDrum']],
    'Effekte':     [['Hall', 'Hall-Effekt'], ['Effekte']],
}

# Lookups
FAMILY_INDEX = {fam: i for i, fam in enumerate(INSTRUMENT_FAMILIES)}
INSTRUMENT_TO_FAMILY = {
    instr: fam
    for fam, groups in INSTRUMENT_FAMILIES.items()
    for instr in _family_members(groups)
}
# Äquivalenzgruppe pro Instrument (aus den inneren Listen)
INSTRUMENT_TO_EQUIV = {}
for groups in INSTRUMENT_FAMILIES.values():
    for group in groups:
        group_set = set(group)
        for instr in group:
            INSTRUMENT_TO_EQUIV[instr] = group_set

DEFAULT_NIVEAU = 0.25   # kleiner = Distraktoren noch stärker aus Nachbarfamilien
NIVEAU_STEP = 0.15
WEIGHT_FLOOR = 0.02   # Restwahrscheinlichkeit für ferne Instrumente (nie exakt 0)



def get_family(instr):
    return INSTRUMENT_TO_FAMILY.get(normalize_instrument_name(instr))

def family_distance(a, b):
    ia, ib = FAMILY_INDEX.get(get_family(a)), FAMILY_INDEX.get(get_family(b))
    if ia is None or ib is None:
        return None
    return abs(ia - ib)

def family_weight(candidate, reference, decay=None):
    if decay is None:
        decay = 1 - DEFAULT_NIVEAU
    d = family_distance(candidate, reference)
    if d is None:
        return WEIGHT_FLOOR
    return max(WEIGHT_FLOOR, decay ** d)

def are_equivalent(a, b):
    a, b = normalize_instrument_name(a), normalize_instrument_name(b)
    if a == b:
        return True
    return b in INSTRUMENT_TO_EQUIV.get(a, {a})

def family_decay_weight(norm, target, decay):
    """Wie family_weight, aber OHNE WEIGHT_FLOOR – sauberer Gradient für find_instrument."""
    d = family_distance(norm, target)
    if d is None:
        d = 6  # unbekannte Familie = "ziemlich weit"
    return decay ** d

def count_weight(norm):
    """Anzahlsgewicht der Äquivalenzgruppe: 4. Wurzel der Beispielanzahl."""
    group = INSTRUMENT_TO_EQUIV.get(norm, {norm})
    return EQUIV_COUNT_WEIGHT.get(frozenset(group), 0.0)

def pick_weighted_instrument_names(references, amount, exclude=None):
    """Namensbasierte Auswahl (für test.html-Distraktoren, die keine echte Audiodatei brauchen)."""
    if not isinstance(references, (list, set, tuple)):
        references = [references]
    ref_norms = [normalize_instrument_name(r) for r in references]
    exclude_norms = {normalize_instrument_name(e) for e in (exclude or [])}

    candidates = {
        normalize_instrument_name(instr)
        for subdict in music_files.values()
        for nick in subdict.values()
        for instr in nick.get('instruments', [])
    }

    chosen, chosen_norms = [], set()
    for _ in range(amount):
        pool = [
            c for c in candidates
            if c not in exclude_norms and c not in chosen_norms
            and not any(are_equivalent(c, r) for r in ref_norms)
            and not any(are_equivalent(c, ch) for ch in chosen_norms)
        ]
        if not pool:
            break
        weights = [max(family_weight(c, r) for r in ref_norms) for c in pool]
        pick = random.choices(pool, weights=weights, k=1)[0]
        chosen.append(pick)
        chosen_norms.add(pick)
    return chosen






















app.config['INSTRUMENT_ORDER'] = [
    instr for groups in INSTRUMENT_FAMILIES.values() for instr in _family_members(groups)
]

app.config['FX'] = ['Gitarren-Amp', 'Bass-Amp', 'Hall']

base_dir = os.path.abspath(os.path.dirname(__file__))
music_directory = os.path.join(base_dir, 'static', 'music')
instrument_directory = os.path.join(base_dir, 'static', 'instruments')
effects_directory = os.path.join(base_dir, 'static', 'effects')
music_files = sort_music_files(parse_music_files(music_directory))

# Anzahl Audio-Beispiele je normalisiertem Instrument
INSTRUMENT_COUNTS = {}
for _subdict in music_files.values():
    for _nick in _subdict.values():
        for _instr in _nick.get('instruments', []):
            _norm = normalize_instrument_name(_instr)
            INSTRUMENT_COUNTS[_norm] = INSTRUMENT_COUNTS.get(_norm, 0) + 1

# Anzahlsgewicht je Äquivalenzgruppe = 4. Wurzel der summierten Beispiele.
# key = frozenset der Gruppe (aus den inneren Listen von INSTRUMENT_FAMILIES)
EQUIV_COUNT_WEIGHT = {}
for _groups in INSTRUMENT_FAMILIES.values():
    for _group in _groups:
        _n = sum(INSTRUMENT_COUNTS.get(g, 0) for g in _group)
        EQUIV_COUNT_WEIGHT[frozenset(_group)] = _n ** 0.25 if _n > 0 else 0.0

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
    instrument_data = get_instrument_data(sorted_instruments, [primary_instrument])
    metadata = track_info.get('metadata', {})

    if  debug:
        print(f"rendering an instrument test with instruments {sorted_instruments} and data: {instrument_data}")
    return render_template('test.html', difficulty='einzel', nickname=nickname, genre=genre, instruments=instrument_data, metadata=metadata, music_directory=os.path.join(music_directory, genre))




@app.route('/find_instrument')
def find_instrument():
    # Adaptiver Zustand aus Query-Parametern
    try:
        niveau = float(request.args.get('niveau', DEFAULT_NIVEAU))
    except (TypeError, ValueError):
        niveau = DEFAULT_NIVEAU
    try:
        run = int(request.args.get('run', 1))
    except (TypeError, ValueError):
        run = 1
    niveau = max(0.0, min(1.0, niveau))
    run = max(1, run)

    # Höheres Niveau -> kleinerer Decay -> Distraktoren aus näheren Familien -> schwerer
    effective_decay = max(0.05, 1.0 - niveau)

    # Flache Liste aller Stems: (genre, nickname, instrument)
    stem_pool = [
        (genre, nickname, instr)
        for genre, tracks in music_files.items()
        for nickname, info in tracks.items()
        for instr in info.get('instruments', [])
    ]
    if not stem_pool:
        return "Keine Musikdateien gefunden.", 404

    by_instrument = {}
    for stem in stem_pool:
        norm = normalize_instrument_name(stem[2])
        by_instrument.setdefault(norm, []).append(stem)

    target = random.choice(list(by_instrument.keys()))
    correct_stem = random.choice(by_instrument[target])

    # Distraktoren: je Äquivalenzgruppe genau EINMAL (sonst zählt eine Gruppe
    # mit mehreren Namen wie Drums/Drumset doppelt), gewichtet nach
    # Familiennähe (adaptiver Decay, floor-frei) × Anzahlsgewicht (4. Wurzel).
    seen_groups = set()
    candidates = []
    for n in by_instrument.keys():
        if are_equivalent(n, target):
            continue
        key = frozenset(INSTRUMENT_TO_EQUIV.get(n, {n}))
        if key in seen_groups:
            continue
        seen_groups.add(key)
        candidates.append(n)

    distractors = []
    while candidates and len(distractors) < 3:
        weights = [
            family_decay_weight(n, target, effective_decay) * count_weight(n)
            for n in candidates
        ]
        pick_norm = random.choices(candidates, weights=weights, k=1)[0]
        candidates.remove(pick_norm)

        # Stem aus der gesamten Äquivalenzgruppe wählen (nicht nur aus einem Namen)
        group = INSTRUMENT_TO_EQUIV.get(pick_norm, {pick_norm})
        group_stems = [s for g in group for s in by_instrument.get(g, [])]
        distractors.append(random.choice(group_stems))

    chosen = [correct_stem] + distractors
    options = []
    for genre, nickname, instr in chosen:
        options.append({
            'genre': genre,
            'nickname': nickname,
            'instrument': instr,
            'image': image_exists(instr),
            'is_correct': (genre, nickname, instr) == correct_stem,
        })
    random.shuffle(options)

    return render_template(
        'find.html',
        target=target,
        target_image=image_exists(target),
        options=options,
        niveau=niveau,
        run=run,
        niveau_step=NIVEAU_STEP,
    )



if __name__ == '__main__':
    app.run(debug=False)