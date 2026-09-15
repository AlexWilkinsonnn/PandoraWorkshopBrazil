import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
import random

# ======================================================================================================================================================
# Plot 1
# ======================================================================================================================================================

def plot1(time_array, pe_array) :
    fig, ax = plt.subplots()
    plt.hist(time_array, bins=100, range=[-10, 10], weights=pe_array)
    #ax.set_yscale('log')
    ax.set_ylim([0,1000])
    ax.set_ylabel('Intensity')
    ax.set_xlabel('Time [µs]')
    plt.show()

# ======================================================================================================================================================
# Plot 2
# ======================================================================================================================================================

def plot2(time_array, width_array, pe_array, mc_time_array, mc_pdg_array, mc_michel_array) :
    
    # Time axis
    time = np.linspace(-1, 10, 5000)

    # Total intensity
    intensity = np.zeros_like(time)

    for pe, t_start, width in zip(pe_array, time_array, width_array):
    
        if width <= 0 or pe <= 0:
            continue
    
        # Exponential decay constant
        tau = width
    
        # Normalise so that integral = PE
        A = pe / tau
    
        # One-sided exponential
        mask = time >= t_start
    
        intensity[mask] += A * np.exp(-(time[mask] - t_start) / tau)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))

    for (mc_time, mc_pdg, is_michel) in zip(mc_time_array, mc_pdg_array, mc_michel_array) :

        if ((abs(mc_pdg) == 14) or (abs(mc_pdg) == 12) or (abs(mc_pdg) == 2112)) :
            continue

        ax.axvline(mc_time, linestyle='--', linewidth=1, label=mc_pdg, color=f'#{random.randint(0, 0xFFFFFF):06x}')

    ax.plot(time, intensity)
    ax.set_xlabel("Time [µs]")
    ax.set_ylabel("Intensity")
    ax.set_xlim(-1, 10)
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.show()

# ======================================================================================================================================================
# Plot 3
# ======================================================================================================================================================

def get_pe(time_array, y_array, z_array, pe_array, pmt_positions, target_time, window):

    time_mask = (
        (time_array >= target_time - window / 2) &
        (time_array <  target_time + window / 2)
    )

    selected_y = y_array[time_mask]
    selected_z = z_array[time_mask]
    selected_pe = pe_array[time_mask]

    pe_values = np.zeros(len(pmt_positions))
    
    for i, (y, z) in enumerate(pmt_positions):
        pmt_mask = (np.isclose(selected_y, y) & np.isclose(selected_z, z))
        pe_values[i] = np.sum(selected_pe[pmt_mask])

    return pe_values

def plot3(Y, Z, PE, TIME, MCX, MCY, MCZ, MCT, t_min=0.0, t_max=10.0, time_window=0.1, threshold_pe=0.03, z_max=500) :

    # ==================================================
    # Flatten/sort MC points by time
    # ==================================================
    # This ensures the dots appear in chronological order.
    mc_sort = np.argsort(MCT)
    MCY = MCY[mc_sort]
    MCZ = MCZ[mc_sort]
    MCT = MCT[mc_sort]

    # ==================================================
    # Restrict PMT data to 0–10 μs
    # ==================================================
    data_mask = ((TIME >= t_min) & (TIME <= t_max))
    y_array = Y[data_mask]
    z_array = Z[data_mask]
    pe_array = PE[data_mask]
    time_array = TIME[data_mask]

    # ==================================================
    # Unique PMT positions
    # ==================================================
    pmt_positions = np.unique(np.stack((Y, Z), axis=1), axis=0)

    # ==================================================
    # Initial PE
    # ==================================================
    initial_pe = get_pe(time_array, y_array, z_array, pe_array, pmt_positions, t_min, time_window)

    # ==================================================
    # Only draw PMTs above threshold
    # ==================================================
    initial_sizes = np.where(initial_pe >= threshold_pe, 50, 0)

    # ==================================================
    # Create figure
    # ==================================================
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlabel("PMT Y position")
    ax.set_ylabel("PMT Z position")

    # ==================================================
    # PMT scatter
    # ==================================================
    sc = ax.scatter(pmt_positions[:, 0],pmt_positions[:, 1], c=initial_pe, s=initial_sizes, vmin=threshold_pe, vmax=z_max)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("PE")

    max_value = np.max(initial_pe) if len(initial_pe) else 0.0
    ax.set_title(
        f"PMT PE at t = {t_min:.2f} μs "
        f"(window = {time_window:.2f} μs, "
        f"{t_min - time_window/2:.2f}–{t_min + time_window/2:.2f} μs)\n"
        f"Maximum PMT PE = {max_value:.3f} "
        f"(threshold_pe = {threshold_pe:.3f})"
    )

    # ==================================================
    # MC positions
    # ==================================================
    initial_mc_mask = (MCT <= t_min)
    mc_positions = ax.scatter(MCY[initial_mc_mask], MCZ[initial_mc_mask], s=25, marker='.', alpha=0.7, label='MC positions')
    ax.legend()

    # ==================================================
    # Time slider
    # ==================================================
    time_slider = widgets.FloatSlider(value=t_min, min=t_min, max=t_max, step=0.01, description='Time:', continuous_update=True,
        readout_format='.2f', style={'description_width': 'initial'}, layout=widgets.Layout(width='600px'))

    # ==================================================
    # Window slider
    # ==================================================
    window_slider = widgets.FloatSlider(value=time_window, min=0.01, max=1.0, step=0.01, description='Window:', continuous_update=True,
        readout_format='.2f', style={'description_width': 'initial'}, layout=widgets.Layout(width='600px'))

    # ==================================================
    # Update function
    # ==================================================
    
    def update_plot(change=None):
        t = time_slider.value
        window = window_slider.value
        new_pe = get_pe(time_array, y_array, z_array, pe_array, pmt_positions, t, window)

        # ==================================================
        # Only draw PMTs >= threshold
        # ==================================================    
        sizes = np.where(new_pe >= threshold_pe, 50, 0)
        sc.set_array(new_pe)
        sc.set_sizes(sizes)    
    
        # ==================================================
        # Update MC positions
        # ==================================================
        # Show every MC point whose time has been reached.
        mc_mask = (MCT <= t)
        mc_positions.set_offsets(np.column_stack((MCY[mc_mask],MCZ[mc_mask])))
    
        # ==================================================
        # Update title
        # ==================================================
        max_value = np.max(new_pe) if len(new_pe) else 0.0
        ax.set_title(f"PMT PE at t = {t:.2f} μs "
            f"(window = {window:.2f} μs, "
            f"{t - window/2:.2f}–{t + window/2:.2f} μs)\n"
            f"Maximum PMT PE = {max_value:.3f} "
            f"(threshold_pe = {threshold_pe:.3f})"
        )

        # ==================================================
        # Redraw
        # ==================================================
        fig.canvas.draw_idle()

    # ==================================================
    # Connect sliders
    # ==================================================
    time_slider.observe(update_plot, names='value')
    window_slider.observe(update_plot, names='value')

    # ==================================================
    # Display
    # ==================================================
    display(widgets.VBox([time_slider,window_slider]))
    plt.show()

# ======================================================================================================================================================
# Plot 4
# ======================================================================================================================================================

def pe_weighted_pca(y, z, weights):
    """
    Calculate the first principal component of (y, z),
    weighted by PE.

    Returns
    -------
    centroid : array([y0, z0])
        PE-weighted centroid.

    direction : array([dy, dz])
        Unit vector along the first principal component.
    """

    if len(y) < 2 or np.sum(weights) <= 0:
        return None, None

    # --------------------------------------------------
    # PE-weighted centroid
    # --------------------------------------------------
    total_weight = np.sum(weights)

    centroid = np.array([
        np.sum(weights * y) / total_weight,
        np.sum(weights * z) / total_weight
    ])

    # --------------------------------------------------
    # Centre the coordinates
    # --------------------------------------------------
    points = np.column_stack((y, z))
    centred = points - centroid

    # --------------------------------------------------
    # PE-weighted covariance matrix
    # --------------------------------------------------
    covariance = (
        centred.T @ (centred * weights[:, None])
    ) / total_weight

    # --------------------------------------------------
    # Eigenvectors/eigenvalues
    # --------------------------------------------------
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)

    # Largest eigenvalue = first principal component
    direction = eigenvectors[:, np.argmax(eigenvalues)]

    # Normalise just to be safe
    direction = direction / np.linalg.norm(direction)

    return centroid, direction

def plot4(Y, Z, PE, TIME, MCX, MCY, MCZ, MCT, t_min=0.0, t_max=10.0, time_window=0.1, threshold_pe=0.03, z_max=500) :

    # ==================================================
    # Flatten/sort MC points by time
    # ==================================================
    # This ensures the dots appear in chronological order.
    mc_sort = np.argsort(MCT)
    MCY = MCY[mc_sort]
    MCZ = MCZ[mc_sort]
    MCT = MCT[mc_sort]

    # ==================================================
    # Restrict PMT data to 0–10 μs
    # ==================================================
    data_mask = ((TIME >= t_min) & (TIME <= t_max))
    y_array = Y[data_mask]
    z_array = Z[data_mask]
    pe_array = PE[data_mask]
    time_array = TIME[data_mask]

    # ==================================================
    # Unique PMT positions
    # ==================================================
    pmt_positions = np.unique(np.stack((Y, Z), axis=1), axis=0)

    # ==================================================
    # Initial PE
    # ==================================================
    initial_pe = get_pe(time_array, y_array, z_array, pe_array, pmt_positions, t_min, time_window)

    # ==================================================
    # Only draw PMTs above threshold
    # ==================================================
    initial_sizes = np.where(initial_pe >= threshold_pe, 50, 0)

    # ==================================================
    # Create figure
    # ==================================================
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlabel("PMT Y position")
    ax.set_ylabel("PMT Z position")

    # ==================================================
    # PMT scatter
    # ==================================================
    sc = ax.scatter(pmt_positions[:, 0],pmt_positions[:, 1], c=initial_pe, s=initial_sizes, vmin=threshold_pe, vmax=z_max)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("PE")

    max_value = np.max(initial_pe) if len(initial_pe) else 0.0
    ax.set_title(
        f"PMT PE at t = {t_min:.2f} μs "
        f"(window = {time_window:.2f} μs, "
        f"{t_min - time_window/2:.2f}–{t_min + time_window/2:.2f} μs)\n"
        f"Maximum PMT PE = {max_value:.3f} "
        f"(threshold_pe = {threshold_pe:.3f})"
    )
    
    # ==================================================
    # MC positions
    # ==================================================
    initial_mc_mask = (MCT <= t_min)
    mc_positions = ax.scatter(MCY[initial_mc_mask], MCZ[initial_mc_mask], s=25, marker='.', alpha=0.7, label='MC positions')
    ax.legend()

    # ==================================================
    # Time slider
    # ==================================================
    time_slider = widgets.FloatSlider(value=t_min, min=t_min, max=t_max, step=0.01, description='Time:', continuous_update=True,
        readout_format='.2f', style={'description_width': 'initial'}, layout=widgets.Layout(width='600px'))

    # ==================================================
    # PE-weighted PCA line
    # ==================================================

    centroid, direction = pe_weighted_pca(pmt_positions[:, 0], pmt_positions[:, 1], initial_pe)

    # Create an initially empty line
    pca_line, = ax.plot([], [], linewidth=2, label='PE-weighted PCA')

    def update_pca_line(pe_values):
        centroid, direction = pe_weighted_pca(pmt_positions[:, 0], pmt_positions[:, 1], pe_values)

        # Not enough active PMTs for PCA
        if centroid is None:
            pca_line.set_data([], [])
            return

        y_range = np.ptp(pmt_positions[:, 0])
        z_range = np.ptp(pmt_positions[:, 1])

        # Use a generous length
        line_length = 2.0 * np.sqrt(y_range**2 + z_range**2)
        line_parameter = np.array([-line_length,line_length])
        line_points = (centroid[:, None] + direction[:, None] * line_parameter)
        pca_y = line_points[0, :]
        pca_z = line_points[1, :]
        pca_line.set_data(pca_y, pca_z)

    # Draw initial PCA
    update_pca_line(initial_pe)
    ax.legend()
    
    # ==================================================
    # Window slider
    # ==================================================
    window_slider = widgets.FloatSlider(value=time_window, min=0.01, max=1.0, step=0.01, description='Window:', continuous_update=True,
        readout_format='.2f', style={'description_width': 'initial'}, layout=widgets.Layout(width='600px'))

    # ==================================================
    # Update function
    # ==================================================
    
    def update_plot(change=None):
        t = time_slider.value
        window = window_slider.value
        new_pe = get_pe(time_array, y_array, z_array, pe_array, pmt_positions, t, window)

        # ==================================================
        # Only draw PMTs >= threshold
        # ==================================================    
        sizes = np.where(new_pe >= threshold_pe, 50, 0)
        sc.set_array(new_pe)
        sc.set_sizes(sizes)    

        # --------------------------------------------------
        # Update PE-weighted PCA
        # --------------------------------------------------
        update_pca_line(new_pe)
        
        # ==================================================
        # Update MC positions
        # ==================================================
        # Show every MC point whose time has been reached.
        mc_mask = (MCT <= t)
        mc_positions.set_offsets(np.column_stack((MCY[mc_mask],MCZ[mc_mask])))
    
        # ==================================================
        # Update title
        # ==================================================
        max_value = np.max(new_pe) if len(new_pe) else 0.0
        ax.set_title(f"PMT PE at t = {t:.2f} μs "
            f"(window = {window:.2f} μs, "
            f"{t - window/2:.2f}–{t + window/2:.2f} μs)\n"
            f"Maximum PMT PE = {max_value:.3f} "
            f"(threshold_pe = {threshold_pe:.3f})"
        )

        # ==================================================
        # Redraw
        # ==================================================
        fig.canvas.draw_idle()

    # ==================================================
    # Connect sliders
    # ==================================================
    time_slider.observe(update_plot, names='value')
    window_slider.observe(update_plot, names='value')

    # ==================================================
    # Display
    # ==================================================
    display(widgets.VBox([time_slider,window_slider]))
    plt.show()


