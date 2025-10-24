# Statistical Analysis Project

This project provides tools for performing statistical analyses, including a one-way ANOVA test, using Python. It utilizes the `pandas` library for data manipulation and `scipy` for statistical computations.

## Project Structure

```
statistical-analysis-project
├── src
│   ├── __init__.py
│   ├── analysis.py
│   └── main.py
├── tests
│   ├── __init__.py
│   └── test_analysis.py
├── Pipfile
└── README.md
```

## Installation

To set up the project environment, you need to have [Pipenv](https://pipenv.pypa.io/en/latest/) installed. If you don't have it installed, you can do so via pip:

```bash
pip install pipenv
```

Once Pipenv is installed, navigate to the project directory and run:

```bash
pipenv install
```

This will create a virtual environment and install the required dependencies specified in the `Pipfile`.

## Usage

To run the statistical analysis, execute the `main.py` script:

```bash
pipenv run python src/main.py
```

The script will prompt you to provide the path to a CSV file and select the type of statistical test you want to perform. Currently, the project supports a one-way ANOVA test.

## Contributing

Feel free to submit issues or pull requests if you have suggestions for improvements or additional features.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.