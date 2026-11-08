# AstroLab — Exoplanet Transit Explorer

An interactive astronomy data analysis dashboard built using Python and Streamlit.

## Overview

AstroLab explores stellar brightness measurements from NASA's Transiting Exoplanet Survey Satellite (TESS).

The project focuses on Pi Mensae (TIC 261136679), using TESS Sector 1 observations to investigate periodic transit-like signals.

## Features

- Interactive TESS light curve visualization
- Box Least Squares (BLS) periodogram
- Phase-folded light curve
- Transit candidate summary
- Dataset explorer and CSV export
- Automated data validation tests

## Technology Stack

- Python
- NumPy
- Pandas
- Astropy (analysis notebooks)
- Lightkurve (data retrieval)
- Plotly
- Streamlit
- Pytest

## Data Source

NASA TESS observations, retrieved from the Mikulski Archive for Space Telescopes (MAST).

Target: Pi Mensae (TIC 261136679)

Sector: 1

Flux product: SPOC PDCSAP

## Installation

1. Clone or download the repository.
2. Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Start the dashboard:

```bash
python -m streamlit run app.py
```

4. Open the local URL shown in the terminal.

## Testing

```bash
python -m pytest -v
```

## Scientific Limitations

The dashboard presents preliminary transit candidate analysis based on a limited TESS observation window. BLS results may be affected by noise, stellar variability, instrumental systematics, period aliases, and preprocessing choices.

The project does not claim a new exoplanet discovery.

## Future Improvements

- Support additional TESS targets and sectors
- Add user-uploaded light curves
- Implement interactive BLS parameter selection
- Include transit model fitting and uncertainty estimation
- Develop an astronomy research API
