
import os
import glob

def dump_all():
    files = glob.glob('/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/transcript_*.vtt') + \
            glob.glob('/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/transcript_*.srt') + \
            glob.glob('/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/*.vtt')
            
    with open('/Users/marcolemoglie_1_2/Desktop/canale/scratch/all_transcripts_dump.txt', 'w', encoding='utf-8') as out:
        for f in files:
            sid = os.path.basename(f).replace('transcript_', '').replace('.vtt', '').replace('.srt', '').split(' [')[0]
            # Handle the date-titled ones
            if '[' in f:
                sid = f.split('[')[1].split(']')[0]
                
            out.write(f"--- SHORT_ID: {sid} ---\n")
            with open(f, 'r', encoding='utf-8') as tf:
                content = tf.read()
                # Remove timestamps and line numbers (rough cleaning)
                content = '\n'.join([l for l in content.split('\n') if not l.strip().isdigit() and '-->' not in l and l.strip()])
                out.write(content + "\n\n")

if __name__ == '__main__':
    dump_all()
