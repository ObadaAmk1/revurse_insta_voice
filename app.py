from flask import Flask, request, send_file, render_template, jsonify
import librosa
import soundfile as sf
import os
import warnings

warnings.filterwarnings('ignore')

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قاموس يحتوي على قيم عكس الفلاتر (تحتاج إلى تجربة دقيقة لضبط الأرقام 100%)
# الفلاتر التي تعتمد على الـ Pitch
REVERSE_EFFECTS = {
    'Princess': {'type': 'pitch', 'steps': -4.5},
    'Chipmunk': {'type': 'pitch', 'steps': -7.0},
    'Demon': {'type': 'pitch', 'steps': 6.0},
    'Grandpa': {'type': 'pitch', 'steps': 2.5},
    'Grandma': {'type': 'pitch', 'steps': -2.5}
}

def reverse_audio_effect(input_path, output_path, effect_name):
    y, sr = librosa.load(input_path, sr=None)
    
    if effect_name in REVERSE_EFFECTS:
        effect = REVERSE_EFFECTS[effect_name]
        if effect['type'] == 'pitch':
            y_processed = librosa.effects.pitch_shift(y, sr=sr, n_steps=effect['steps'])
        else:
            y_processed = y
    else:
        # فلاتر التشويه والصدى (مثل Robot, Stadium, Underwater)
        # لا يمكن عكسها بسهولة باستخدام librosa فقط لأنها فلاتر مدمرة (Destructive)
        # نعيد الصوت كما هو مؤقتاً أو يمكن إضافة خوارزميات إزالة صدى لاحقاً
        y_processed = y 
        
    sf.write(output_path, y_processed, sr)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files or 'effect' not in request.form:
        return jsonify({"error": "بيانات مفقودة"}), 400
        
    file = request.files['file']
    effect = request.form['effect']
    
    input_path = os.path.join(UPLOAD_FOLDER, 'input_audio.wav')
    output_path = os.path.join(UPLOAD_FOLDER, 'output_audio.wav')
    
    file.save(input_path)
    
    try:
        reverse_audio_effect(input_path, output_path, effect)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)