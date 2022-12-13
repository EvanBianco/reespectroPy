# Spectral plot
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

import plot_utils


st.subheader("Reflectance spectroscopy explorer")

df = pd.read_csv('merged_data_with_labels.csv', index_col=0)

w = list(np.arange(450, 2500).astype(str))
basis = np.array(w).astype(float)

# --- DATASETS ---
with st.sidebar:
    uploaded_file = st.file_uploader("Choose your own file")
    if uploaded_file is not None:
        # Can be used wherever a "file-like" object is accepted:
        df = pd.read_csv(uploaded_file)
        #st.write(dataframe)
try:
    datasets = tuple(df.dataset.unique())
except:
    datasets = None

# --- MAKE SIDEBAR ---
with st.sidebar:
    st.subheader("Select a sample")


# --- DATASET DATAFRAME ---
if datasets is not None:

    # --- Add dataset selector ---
    dataset_sel = st.sidebar.selectbox(
        'Select a dataset',
        datasets
        )
    df_ds = df[df['dataset'] == dataset_sel]
else:
    st.write('please select a CSV file')
    df_ds = df


# Add a mineral selector to the sidebar
min_sel = st.sidebar.selectbox(
        'Type in or select a mineral',
        sorted(df_ds['Mineral_Name'].unique())
        )


df_min = df_ds.loc[df_ds['Mineral_Name'] == min_sel]

n_samples_mineral = df_min.shape[0]

sample_id = st.sidebar.selectbox(
            f'Select a {min_sel} sample ({n_samples_mineral})',
            sorted(df_min['ID'])
        )

indx = df_min.loc[df_min['ID'] == sample_id].index[0]


# Slider for darkness threshold
dark_flag = st.sidebar.slider(
    'Adjust darkness threshold',
    0.0, 1.0, (0.05),
)


st.sidebar.write(f'Source: URL --> {dataset_sel}', color='blue')


# --- DOWNLOAD THE DATASET ---
if st.sidebar.button('Download the entire data set'):
    st.sidebar.write("Not implemented")
    st.sidebar.write("This does't make sense yet, because we have all the data!")
else:
    st.write(' ')


# --- DISPLAY METADATA ABOVE PLOT --- 
meta_keys=['ID', 'Mineral_Name', 'Formula', 'cm_ree_labels']
for key in meta_keys:
    val = str(df_ds.iloc[indx][key])
    try:
        if key.lower() == 'formula':
            val = plot_utils.format_formula(val)
        st.write(key.replace('s',''), ':  ',  val)
    except:
        st.write(key.replace('s',''), ':  ', 'missing')
meta_df = pd.DataFrame(df_ds.iloc[indx][meta_keys])


if st.button('Classify sample (OUR MACHINE LEARNING BUTTON)'):
    st.write('Not implemented!')
else:
    st.write(' ')


# --- THE MAIN PLOT ---
def spectral_plot(df_ds,
                  indx,
                  dark_flag=0.5,
                  meta_keys=None
                  ):

    # Select the REE collection  
    fig, ax = plot_utils.plot(df_ds.iloc[indx], dark_flag=dark_flag, meta_keys=meta_keys)
    ax.legend()
    return fig


fig = spectral_plot(df_ds, indx, dark_flag=dark_flag, )

# Show figure
st.pyplot(fig)


# Show Meta Data Table
st.table(meta_df.T)


# Download image
if True:
    meta_keys=['ID', 'Mineral_Name', 'Formula']
    fig = spectral_plot(df_ds, indx, dark_flag=dark_flag, meta_keys=meta_keys)
    fname = f'{min_sel}_{sample_id}.png'
    img = io.BytesIO()
    plt.savefig(img, format='png')

    btn = st.download_button(
        label=f'Download image of {min_sel} {sample_id}',
        data=img,
        file_name=fname,
        mime='image/png'
    )


if st.button('Contact us'):
    st.write('Not implemented!')
else:
    st.write(' ')