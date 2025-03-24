# Higher Criticism Project

## Overview
This project implements a data acquisition and text processing pipeline to analyze arXiv papers—focusing on topics such as authorship attribution, word frequency trends, and higher criticism methods. The repository includes scripts for:

- **Data Acquisition:** Downloading arXiv metadata and (optionally) full PDF content.
- **Text Processing:** Performing advanced text cleaning including tokenization, LaTeX command removal, stopword removal, and lemmatization.
- **Dataset Creation:** Generating multiple datasets:
  1. **arxiv_march_data.json:** Raw arXiv metadata (without PDFs).
  2. **arxiv_march_data_with_pdf.json:** Metadata with downloaded PDF content.
  3. **arxiv_march_data_with_processed_summary.json:** Processed summaries (derived from Dataset 1).
  4. **arxiv_march_data_with_processed_summary_and_pdf.json:** Processed summaries and PDFs (derived from Dataset 2).
- **Data Analysis & Visualization:** Notebooks to visualize metrics such as the number of papers per year, category distributions, and trends in top words. For example, one notebook creates a heatmap showing the top 10 frequent words per year for easy comparison across years.

## Repository Structure
Higher-Criticism-Project/ ├── data/ │ ├── arxiv_march_data.json │ ├── arxiv_march_data_with_pdf.json │ ├── arxiv_march_data_with_processed_summary.json │ └── arxiv_march_data_with_processed_summary_and_pdf.json ├── notebooks/ │ └── analysis.ipynb # Jupyter Notebook for data analysis and visualization ├── src/ │ ├── arxiv_data.py # Data acquisition functions (using arXiv API) │ └── text_processing.py # Advanced text processing functions ├── requirements.txt └── README.md


## Setup and Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your_username/Higher-Criticism-Project.git
   cd Higher-Criticism-Project

2. Create a Virtual Environment (Optional but recommended):

python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

3. Install Dependencies:
pip install -r requirements.txt

4. Download NLTK Data: In a Python shell or within your Jupyter Notebook, run:
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

Usage
Data Acquisition
Run the scripts in src/arxiv_data.py to fetch arXiv metadata and (optionally) download PDF content. This will generate:

data/arxiv_march_data.json

data/arxiv_march_data_with_pdf.json

Data Processing
Use the functions in src/text_proces
sing.py to process summaries and PDF content.

This step creates:

data/arxiv_march_data_with_processed_summary.json

data/arxiv_march_data_with_processed_summary_and_pdf.json

Data Analysis and Visualization
Open the notebook notebooks/analysis.ipynb to explore and visualize the data.

Visualizations include:

Number of papers per year.

Stacked bar charts of the top 30 categories per year (with categories simplified, e.g., "math.DS" becomes "math").

A heatmap showing the top 10 frequent words per year, making it easy to compare trends across years.

Advanced Instructions
Category Simplification:
Categories such as "math.DS" or "math-DS" are simplified to "math" by splitting on periods and dashes. This allows grouping all math-related papers together.

Optimizing Large Datasets:
If your datasets are very large, consider processing them incrementally or using a streaming JSON parser (like ijson) to avoid memory crashes.

Visualization Customization:
The provided visualizations use Matplotlib and Seaborn. You can modify the color maps, layout, or filtering criteria (e.g., displaying only the top 30 categories) to suit your analysis needs.

Contributing
Contributions, issues, and feature requests are welcome! Please check the issues page.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgements
Thanks to the arXiv API for providing a rich corpus of research papers.

Inspired by research in higher criticism and authorship attribution.

pgsql
Copy


