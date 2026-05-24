from flask import Flask, request, send_file, render_template, jsonify
import librosa
import soundfile as sf
import os
import warnings
from werkzeug.utils import secure_filename
from moviepy.editor import AudioFileClip

warnings.filterwarnings('ignore')

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# فلاتر إنستغرام ودرجات التعديل
REVERSE_EFFECTS = {
    'Princess': {'type': 'pitch', 'steps': -4.5},
    'Chipmunk': {'type': 'pitch', 'steps': -7.0},
    'Demon': {'type': 'pitch', 'steps': 6.0},
    'Grandpa': {'type': 'pitch', 'steps': 2.5},
    'Grandma': {'type': 'pitch', 'steps': -2.5}
}

def process_media_file(input_path, output_path, effect_name):
    temp_wav = os.path.join(UPLOAD_FOLDER, 'temp_audio.wav')
    
    # 1. استخراج الصوت من أي فيديو أو ملف صوتي وتحويله إلى WAV
    try:
        audio_clip = AudioFileClip(input_path)
        audio_clip.write_audiofile(temp_wav, logger=None)
        audio_clip.close()
    except Exception as e:
        raise Exception("فشل في قراءة الملف. تأكد أنه ملف صوت أو فيديو يعمل بشكل صحيح.")

    # 2. تحميل الصوت النقي لمعالجته
    y, sr = librosa.load(temp_wav, sr=None)
    
    # 3. تطبيق المعالجة وعكس الفلتر
    if effect_name in REVERSE_EFFECTS:
        steps = REVERSE_EFFECTS[effect_name]['steps']
        y_processed = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
    else:
        y_processed = y 
        
    # 4. حفظ النتيجة النهائية
    sf.write(output_path, y_processed, sr)
    
    # 5. تنظيف الملف المؤقت
    if os.path.exists(temp_wav):
        os.remove(temp_wav)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files or 'effect' not in request.form:
        return jsonify({"error": "بيانات مفقودة"}), 400
        
    file = request.files['file']
    effect = request.form['effect']
    
    if file.filename == '':
        return jsonify({"error": "لم يتم اختيار ملف"}), 400

    # الحفاظ على صيغة الملف الأصلية (ضروري جداً للفيديوهات)
    original_filename = secure_filename(file.filename)
    if not original_filename:
        original_filename = "upload.media"
        
    input_path = os.path.join(UPLOAD_FOLDER, original_filename)
    output_path = os.path.join(UPLOAD_FOLDER, 'reversed_audio.wav')
    
    file.save(input_path)
    
    try:
        process_media_file(input_path, output_path, effect)
        
        # تنظيف ملف الفيديو/الصوت الأصلي بعد الانتهاء
        if os.path.exists(input_path):
            os.remove(input_path)
            
        return send_file(output_path, as_attachment=True, download_name="reversed_audio.wav")
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
