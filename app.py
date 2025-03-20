import os
from flask import Flask, request, render_template, send_file
import pdfkit
import logging

# Inițializează aplicația Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Specifică calea către executabilul wkhtmltopdf
path_wkhtmltopdf = 'D:/Storage/Treburi/wkhtmltox/bin/wkhtmltopdf.exe'  # Actualizează această cale
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

        # Adaugă footerul la date
        footer_html = render_template('footer.html', data=data)
        footer_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'footer.html')
        with open(footer_file_path, 'w', encoding='utf-8') as f:
            f.write(footer_html)
        logging.debug(f"Footer HTML: {footer_html}")

        # Adaugă headerul la date
        header_html = render_template('header.html', data=data)
        header_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'header.html')
        with open(header_file_path, 'w', encoding='utf-8') as f:
            f.write(header_html)
        logging.debug(f"Header HTML: {header_html}")

        rendered = render_template('referat_template.html', data=data)
        logging.debug(f"Rendered HTML: {rendered}")

        pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Referat_de_Necesitate.pdf')
        options = {
            'enable-local-file-access': None,
            'no-stop-slow-scripts': None,
            'footer-html': footer_file_path,  # Adaugă footerul din fișierul HTML
            'header-html': header_file_path,  # Adaugă headerul din fișierul HTML
            'encoding': 'UTF-8'  # Asigură-te că encoding-ul este corect pentru diacritice
        }
        pdfkit.from_string(rendered, pdf_file_path, configuration=config, options=options)
        logging.debug(f"PDF generated at: {pdf_file_path}")

        return send_file(pdf_file_path, as_attachment=True)
    
    return render_template('index.html', institutii=institutii)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)