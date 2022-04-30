import csv
import json


# RUN THIS TO CREATE static/harmonies.json from harmonies.csv.

# harmonies = (key_set_0, key_set_1, ... , key_set_11)
# Indices 0-11 in harmonies are tonal centers with 0 representing "C".

# key_set_X = {harmony_group_key: harmony_group, harmony_group_key: harmony_group, ...}
# Key_set can be empty, indicating no harmonies in key.

# harmony_group = [harmony, harmony, ...]
# Groups similar harmonies together.

# harmony = (chord_symbol_a, chord_symbol_b, chord_symbol_c, note_a, note_b, note_c)
# A specific variation of the harmonies within this harmony_group.
# Chord_symbol_a is an integer representing the chord root relative to the given top note.
# Chord_symbol_b is a string placed after the chord root, usually empty or "min" for minor chords.
# Chord_symbol_c is a string placed last in superscript, usually indicating chord extensions/alterations.
# Note values are integers representing how many midi notes (half steps) they are below the given top note.
# Note_a is first note below the given top note. The other notes follow in decending order.


harmonies = [{} for _ in range(12)]
with open('harmonies.csv', newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    skip_row = True
    for row in csv_reader:
        if skip_row:  # Skip first row.
            skip_row = False
            continue
        key_set = int(row[0])
        harmony_group = int(row[1])
        chord_a = int(row[2])
        chord_b = str(row[3])
        chord_c = str(row[4])
        note_a = int(row[5])
        note_b = int(row[6])
        note_c = int(row[7])
        harmony = [chord_a, chord_b, chord_c, note_a, note_b, note_c]
        if harmony_group in harmonies[key_set]:
            harmonies[key_set][harmony_group].append(harmony)
        else:
            harmonies[key_set][harmony_group] = [harmony]
with open(f"static/harmonies.json", "w") as file:
    json.dump(harmonies, file)
