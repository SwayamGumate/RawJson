# RawJson - Raw Data to JSON & Table Converter

RawJson is a comprehensive, production-quality web application designed to seamlessly convert raw, unstructured text data (like key-value pairs or CSVs) into formatted JSON, and transform JSON arrays into clean, structured HTML tables.

Built with Python (Flask) and a zero-dependency Vanilla JS/CSS frontend, RawJson is lightweight, incredibly fast, and features a premium modern UI.

## Features ✨
- **Intelligent Formatting**: Parses standard JSON, CSV data, strict `key: value` pair lists, and even malformed Javascript objects.
- **Dynamic Table Generation**: Utilizes the power of `pandas` to instantly convert lists of objects into beautifully aligned HTML data tables.
- **File Upload Support**: Directly process data from `.txt`, `.csv`, and `.json` files.
- **Export & Copy**: Quick action buttons to copy outputs to clipboard, or download them directly as `.json` or `.csv` files.
- **Premium UI/UX**: Fully responsive, mobile-friendly design with an integrated Dark Mode toggle and loading states.
- **Sample Data**: Built-in sample data generation to quickly test capabilities.

## Tech Stack 🛠️
- **Backend**: Python 3, Flask
- **Data Processing**: Pandas, Built-in `json` and `re` modules
- **Frontend**: HTML5, Vanilla CSS3 (with Custom Properties for theming), Vanilla JavaScript

## Project Structure 📁
```
RawJson/
│
├── app.py               # Main Flask server and routes
├── utils.py             # Data transformation utilities
├── requirements.txt     # Python dependencies
│
├── static/
│   ├── css/
│   │   └── style.css    # Premium styling with dark mode support
│   └── js/
│       └── main.js      # Fetch API logic and DOM manipulation
│
└── templates/
    └── index.html       # Application interface
```

## Setup Instructions 🚀

1. Ensure you have Python 3.8+ installed.
2. Navigate to your project directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Flask development server:
   ```bash
   python app.py
   ```
5. Open your web browser and navigate to `http://127.0.0.1:5000`.

## Built With ♥️
Ready to be added to your developer portfolio!
