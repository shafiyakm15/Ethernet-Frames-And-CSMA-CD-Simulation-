


import tkinter as tk
from tkinter import ttk
import random
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Constants
NUM_NODES = 5
MAX_ATTEMPTS = 50
DATA_PER_SUCCESS = 1500 * 8  # bits (1500 bytes)

# Tracking lists
backoff_history = []
success_per_device = [0 for _ in range(NUM_NODES)]
channel_utilization = []
collision_times = []
bandwidth_log = []
time_log = []
data_sent_log = []

def run_simulation():
    collision_count = 0
    successful_transmissions = 0
    total_attempts = 0
    total_data_sent = 0
    backoff_times = []

    result_text.delete(1.0, tk.END)
    start_time = time.time()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        total_attempts += 1
        log(f"\nAttempt {attempt}:")
        transmit_slots = [random.randint(0, 1) for _ in range(NUM_NODES)]
        log(f"Node decisions: {transmit_slots}")

        transmitting = transmit_slots.count(1)
        channel_utilization.append(transmitting)

        if transmitting == 1:
            index = transmit_slots.index(1)
            log("✅ Successful transmission!")
            success_per_device[index] += 1
            successful_transmissions += 1
            total_data_sent += DATA_PER_SUCCESS
            elapsed = time.time() - start_time
            bandwidth = total_data_sent / elapsed if elapsed > 0 else 0
            bandwidth_log.append(bandwidth / 1_000_000)  # Mbps
            time_log.append(attempt)
            data_sent_log.append(total_data_sent)
            backoff_history.append(0)
            break
        elif transmitting > 1:
            log("💥 Collision detected!")
            collision_times.append(attempt)
            collision_count += 1
            backoff = random.randint(100, 1000)
            backoff_times.append(backoff)
            log(f"⏳ Backing off for {backoff} ms...")
            time.sleep(backoff / 1000.0)
            backoff_history.append(backoff)
        else:
            log("🟡 No transmission")
            backoff_history.append(0)

        progress['value'] = (attempt / MAX_ATTEMPTS) * 100
        root.update_idletasks()

    end_time = time.time()
    duration = end_time - start_time
    avg_backoff = sum(backoff_times) / len(backoff_times) if backoff_times else 0
    efficiency = (successful_transmissions / total_attempts) * 100
    bandwidth_final = total_data_sent / duration if duration > 0 else 0
    bandwidth_log.append(bandwidth_final / 1_000_000)
    time_log.append(total_attempts)

    # Final output
    log("\n📊 Final Results:")
    log(f"Total Attempts: {total_attempts}")
    log(f"Collisions: {collision_count}")
    log(f"Avg Backoff Time: {avg_backoff:.2f} ms")
    log(f"Efficiency: {efficiency:.2f}%")
    log(f"Simulated Bandwidth: {bandwidth_final / 1_000_000:.3f} Mbps")

    draw_all_graphs()

def log(message):
    result_text.insert(tk.END, message + "\n")
    result_text.see(tk.END)

def draw_all_graphs():
    for widget in graph_frame.winfo_children():
        widget.destroy()

    fig = Figure(figsize=(13, 10), dpi=100)
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.2])

    title_font = {'fontsize': 12, 'fontweight': 'bold'}
    label_font = {'fontsize': 10}

    # Subplot 1: Backoff Time Evolution
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(range(1, len(backoff_history)+1), backoff_history, marker='o', color='blue')
    ax1.set_title("Backoff Time Evolution", **title_font)
    ax1.set_xlabel("Attempt", **label_font)
    ax1.set_ylabel("Backoff Time (ms)", **label_font)
    ax1.grid(True)

    # Subplot 2: Successful Transmissions
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.bar(range(NUM_NODES), success_per_device, color='steelblue')
    ax2.set_title("Successful Transmissions per Device", **title_font)
    ax2.set_xlabel("Device ID", **label_font)
    ax2.set_ylabel("Success Count", **label_font)
    ax2.grid(True, axis='y')

    # Subplot 3: Channel Utilization
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(range(1, len(channel_utilization)+1), channel_utilization, marker='o', linestyle='-', color='purple')
    ax3.set_title("Channel Utilization Over Time", **title_font)
    ax3.set_xlabel("Time Slot", **label_font)
    ax3.set_ylabel("Devices Transmitting", **label_font)
    ax3.grid(True)

    # Subplot 4: Collision Frequency
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.hist(collision_times, bins=10, color='red', edgecolor='black')
    ax4.set_title("Collision Frequency Over Time", **title_font)
    ax4.set_xlabel("Time Slot", **label_font)
    ax4.set_ylabel("Collision Count", **label_font)
    ax4.grid(True)

    # Subplot 5: Simulated Bandwidth Over Time (full row)
    ax5 = fig.add_subplot(gs[2, :])
    ax5.plot(time_log, bandwidth_log, color='green', marker='D')
    ax5.set_title("Simulated Bandwidth Over Time", **title_font)
    ax5.set_xlabel("Attempt", **label_font)
    ax5.set_ylabel("Bandwidth (Mbps)", **label_font)
    ax5.grid(True)

    fig.tight_layout(pad=3)

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def start_simulation():
    start_button.config(state=tk.DISABLED)
    run_simulation()
    start_button.config(state=tk.NORMAL)

# GUI Setup
root = tk.Tk()
root.title("CSMA/CD Simulation – Embedded Graphs + Bandwidth")
root.geometry("1280x900")
root.configure(bg="#f0f0f0")

tk.Label(root, text="Ethernet CSMA/CD Protocol Simulation with Graphs and Bandwidth",
         font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

start_button = ttk.Button(root, text="Start Simulation", command=start_simulation)
start_button.pack(pady=5)

progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=800, mode='determinate')
progress.pack(pady=10)

result_text = tk.Text(root, height=10, width=130, font=("Courier", 10))
result_text.pack(pady=10)

graph_frame = tk.Frame(root, bg="white", bd=2, relief=tk.SUNKEN)
graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()




