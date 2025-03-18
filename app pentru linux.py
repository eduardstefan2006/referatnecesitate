import os
from flask import Flask, request, render_template, send_file
import pdfkit
import logging

# Inițializează aplicația Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Specifică calea către executabilul wkhtmltopdf
path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'  # Actualizează această cale pentru Linux
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# Configurează logarea
logging.basicConfig(level=logging.DEBUG)

# Asigură-te că folderul de încărcări există
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    institutii = [
        'ȘCOALA GIMNAZIALĂ NR.1 LIEȘTI',
        'ȘCOALA GIMNAZIALĂ NR.2 LIEȘTI',
        'ȘCOALA GIMNAZIALĂ „SFÂNTUL NICOLAE” LIEȘTI'
    ]
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        logging.debug(f"Form data received: {data}")

        # Elimină '[]' din cheile dicționarului
        data = {key.replace('[]', ''): value for key, value in data.items()}

        # Calculează valorile pentru 'nr_crt' și 'valoare'
        for i in range(len(data.get('product_0', []))):
            data['product_0'][i] = str(i + 1)  # Nr. Crt.
            try:
                cantitate = float(data['product_3'][i])
                pret_unitar = float(data['product_4'][i])
                data['product_5'][i] = f"{cantitate * pret_unitar:.2f}"  # Valoare
                logging.debug(f"Calculated values for row {i+1}: cantitate={cantitate}, pret_unitar={pret_unitar}, valoare={data['product_5'][i]}")
                data['product_3'][i] = f"{cantitate:.2f}"  # Cantitate
                data['product_4'][i] = f"{pret_unitar:.2f}"  # Pret unitar
            except ValueError:
                data['product_5'][i] = ''  # Gestionare input invalid

        logging.debug(f"Processed data: {data}")

        rendered = render_template('referat_template.html', data=data)
        logging.debug(f"Rendered HTML: {rendered}")

        pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Referat_de_Necesitate.pdf')
        options = {
            'enable-local-file-access': None,
            'no-stop-slow-scripts': None
        }
        pdfkit.from_string(rendered, pdf_file_path, configuration=config, options=options)
        logging.debug(f"PDF generated at: {pdf_file_path}")

        return send_file(pdf_file_path, as_attachment=True)
    
    data = {
        'nr_inregistrare': ['001'],
        'data': ['2025-02-13'],
        'institutia': [''],
        'subsemnatul': [''],
        'angajat_al': [''],
        'functia': [''],
        'motivare': [''],
        'product_0': [1, 2, 3],
        'product_1': ['Produs 1', 'Produs 2', 'Produs 3'],
        'product_2': ['Buc', 'Buc', 'Buc'],
        'product_3': [10.00, 20.00, 30.00],
        'product_4': [15.00, 25.00, 35.00],
        'product_5': [150.00, 500.00, 1050.00]
    }
    return render_template('index.html', data=data, institutii=institutii)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)