# PDFProva

PDFProva is a Django-based platform designed for converting and digitally signing PDF documents. It also features an integrated technology blog to share insights and updates related to PDF technology and digital signatures.

## Features

- **PDF Conversion**: Easily upload and convert PDF files with various options.
- **Digital Signing**: Securely sign your PDFs digitally.
- **Technology Blog**: Stay updated with the latest trends and tips in PDF technology.

## Project Structure

```
PDFProva
├── PDFProva
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── converter
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── blog
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates
│   ├── base.html
│   ├── converter
│   │   └── index.html
│   └── blog
│       └── index.html
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
├── manage.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd PDFProva
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage

- Access the PDF conversion feature at `/converter/`.
- Explore the technology blog at `/blog/`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.