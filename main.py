import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import bluequbit
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import find_peaks
import time
from datetime import datetime

class EnhancedATHValidator:
    def __init__(self, token: str):
        """Initialize the ATH quantum validator"""
        self.bq = bluequbit.init(token)
        self.shots = 1000  # Each shot costs $0.00145

    def create_falsification_circuit(self, param: float) -> QuantumCircuit:
        """
        Creates a circuit specifically designed to potentially falsify ATH
        Modified to optimize for quantum hardware execution
        """
        qr = QuantumRegister(8, 'q')
        cr = ClassicalRegister(8, 'c')
        qc = QuantumCircuit(qr, cr)

        # Create a GHZ state
        qc.h(qr[0])
        for i in range(7):
            qc.cx(qr[i], qr[i+1])

        # Apply time-dependent phase shifts
        for i in range(8):
            qc.rz(param * np.pi * (i+1), qr[i])

        # Create temporal correlations
        angle = param * np.pi
        for i in range(7):
            qc.crz(angle, qr[i], qr[i+1])
            if i < 6:
                qc.ccx(qr[i], qr[i+1], qr[i+2])
                qc.rz(angle/2, qr[i+2])
                qc.ccx(qr[i], qr[i+1], qr[i+2])

        # Final superposition layer
        for i in range(8):
            qc.h(qr[i])

        qc.measure(qr, cr)
        return qc

    def run_enhanced_validation(self) -> Dict:
        """
        Improved validation with robust error handling and result verification
        """
        results = {
            'falsification': [],
            'beyond_quantum': [],
            'temporal_correlation': []
        }

        param_range = np.linspace(0.1, 2.0, 8)
        retry_delay = 5
        max_retries = 3

        print("\nRunning quantum validation tests...")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Estimated cost: $14.00 (8 jobs × $1.75 each)")

        for idx, param in enumerate(param_range):
            print(f"\nParameter {idx+1}/8: {param:.2f}")
            print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")

            retry_count = 0
            success = False

            while not success and retry_count < max_retries:
                try:
                    # Create and run circuit
                    circuit = self.create_falsification_circuit(param)
                    print(f"Attempt {retry_count + 1}: Submitting job...")
                    
                    # Run with verification
                    result = self.bq.run(circuit, device='quantum', shots=self.shots)
                    if result is None:
                        raise ValueError("Quantum job returned None result")

                    # Try to get top_128_results first
                    if hasattr(result, 'top_128_results'):
                        counts = result.top_128_results
                    else:
                        # Fallback to get_counts
                        counts = result.get_counts()

                    if not counts:
                        raise ValueError("No measurement counts returned")

                    # Calculate metrics with validation
                    try:
                        correlation = self._calculate_temporal_correlation(counts)
                        falsification = self._calculate_falsification_metric(counts)
                        beyond_quantum = self._calculate_beyond_quantum_metric(counts)

                        # Validate metric values
                        if not all(isinstance(x, (int, float)) for x in [correlation, falsification, beyond_quantum]):
                            raise ValueError("Invalid metric calculation")

                        # Store results
                        results['temporal_correlation'].append((param, float(correlation)))
                        results['falsification'].append((param, float(falsification)))
                        results['beyond_quantum'].append((param, float(beyond_quantum)))

                        print("Results successfully collected:")
                        print(f"- Temporal Correlation: {correlation:.3f}")
                        print(f"- Falsification: {falsification:.3f}")
                        print(f"- Beyond Quantum: {beyond_quantum:.3f}")

                        success = True

                    except Exception as e:
                        print(f"Error calculating metrics: {str(e)}")
                        retry_count += 1

                except Exception as e:
                    print(f"Error on attempt {retry_count + 1}: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print("Maximum retries reached, skipping parameter point")
                        # Add null results to maintain array size
                        results['temporal_correlation'].append((param, 0.0))
                        results['falsification'].append((param, 0.0))
                        results['beyond_quantum'].append((param, 0.0))

            time.sleep(2)  # Delay between parameters

        # Validate final results before returning
        if not all(len(v) == len(param_range) for v in results.values()):
            raise ValueError("Incomplete results collected")

        return results

    def _calculate_temporal_correlation(self, counts: Dict[str, int]) -> float:
        """Calculate temporal correlations"""
        if not counts:
            return 0.0
        total = sum(counts.values())
        if total == 0:
            return 0.0
            
        correlation_sum = 0
        for state, count in counts.items():
            bits = [int(x) for x in state]
            for i in range(len(bits)-2):
                if bits[i] == bits[i+1] == bits[i+2]:
                    correlation_sum += count
        return correlation_sum / total

    def _calculate_falsification_metric(self, counts: Dict[str, int]) -> float:
        """Calculate falsification metric"""
        if not counts:
            return 0.0
        total = sum(counts.values())
        if total == 0:
            return 0.0
            
        weight_sum = 0
        for state, count in counts.items():
            bits = [int(x) for x in state]
            local_entropy = sum(bits) / len(bits)
            weight = abs(local_entropy - 0.5) * count
            weight_sum += weight
        return weight_sum / total

    def _calculate_beyond_quantum_metric(self, counts: Dict[str, int]) -> float:
        """Calculate beyond-quantum metric"""
        if not counts:
            return 0.0
        total = sum(counts.values())
        if total == 0:
            return 0.0
            
        pattern_sum = 0
        for state, count in counts.items():
            bits = [int(x) for x in state]
            for i in range(len(bits)-3):
                pattern = bits[i:i+4]
                if pattern == [1,0,1,0] or pattern == [0,1,0,1]:
                    pattern_sum += count
        return pattern_sum / total

    def analyze_enhanced_results(self, results: Dict) -> Dict:
        """
        Improved analysis with robust error handling
        """
        analysis = {}

        # Validate input
        if not results or not all(v for v in results.values()):
            raise ValueError("No valid results to analyze")

        for test_type in results.keys():
            try:
                data = results[test_type]
                if not data:
                    continue

                x_vals = np.array([x for x, _ in data])
                y_vals = np.array([y for _, y in data])

                if len(x_vals) == 0 or len(y_vals) == 0:
                    print(f"No valid data for {test_type}")
                    continue

                # Calculate statistics with error handling
                try:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                except Exception:
                    slope = intercept = r_value = p_value = std_err = np.nan

                try:
                    peaks, _ = find_peaks(y_vals)
                    peak_values = y_vals[peaks] if len(peaks) > 0 else []
                except Exception:
                    peak_values = []

                try:
                    fft_vals = np.abs(np.fft.fft(y_vals))
                    main_freq = np.fft.fftfreq(len(y_vals))[np.argmax(fft_vals[1:])+1]
                except Exception:
                    main_freq = np.nan

                analysis[test_type] = {
                    'mean': float(np.mean(y_vals)),
                    'sem': float(stats.sem(y_vals)) if len(y_vals) > 1 else np.nan,
                    'r_squared': float(r_value**2) if not np.isnan(r_value) else np.nan,
                    'p_value': float(p_value) if not np.isnan(p_value) else np.nan,
                    'slope': float(slope) if not np.isnan(slope) else np.nan,
                    'peaks': [float(p) for p in peak_values],
                    'main_frequency': float(main_freq) if not np.isnan(main_freq) else np.nan
                }

            except Exception as e:
                print(f"Error analyzing {test_type}: {str(e)}")
                analysis[test_type] = {
                    'mean': np.nan,
                    'sem': np.nan,
                    'r_squared': np.nan,
                    'p_value': np.nan,
                    'slope': np.nan,
                    'peaks': [],
                    'main_frequency': np.nan
                }

        return analysis

    def plot_enhanced_results(self, results: Dict):
        """Plot results with improved visualization"""
        # Main results plot
        plt.figure(figsize=(10, 6))
        
        test_types = ['falsification', 'beyond_quantum', 'temporal_correlation']
        colors = ['blue', 'orange', 'green']
        
        for test_type, color in zip(test_types, colors):
            if results[test_type]:
                x_vals = [x for x, _ in results[test_type]]
                y_vals = [y for _, y in results[test_type]]
                plt.plot(x_vals, y_vals, f'-o', color=color, label=test_type.replace('_', ' ').title(),
                        linewidth=2, markersize=8)

        plt.xlabel('Parameter Value')
        plt.ylabel('Metric Value')
        plt.title('ATH Validation Results')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Create second figure with frequency analysis and correlations
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

        # Frequency analysis
        for test_type, color in zip(test_types, colors):
            if results[test_type]:
                y_vals = np.array([y for _, y in results[test_type]])
                fft_vals = np.abs(np.fft.fft(y_vals))
                freqs = np.fft.fftfreq(len(y_vals))
                
                ax1.plot(freqs[1:len(freqs)//2], fft_vals[1:len(fft_vals)//2],
                        color=color, label=test_type.replace('_', ' ').title())

        ax1.set_xlabel('Frequency')
        ax1.set_ylabel('Magnitude')
        ax1.set_title('Frequency Analysis')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Correlation matrix
        correlation_matrix = np.zeros((len(test_types), len(test_types)))
        for i, test1 in enumerate(test_types):
            for j, test2 in enumerate(test_types):
                if results[test1] and results[test2]:
                    y1 = np.array([y for _, y in results[test1]])
                    y2 = np.array([y for _, y in results[test2]])
                    correlation_matrix[i, j] = np.corrcoef(y1, y2)[0, 1]

        im = ax2.imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
        plt.colorbar(im, ax=ax2)
        ax2.set_xticks(range(len(test_types)))
        ax2.set_yticks(range(len(test_types)))
        ax2.set_xticklabels([t.replace('_', ' ').title() for t in test_types], rotation=45)
        ax2.set_yticklabels([t.replace('_', ' ').title() for t in test_types])
        ax2.set_title('Metric Correlations')

        plt.tight_layout()
        plt.show()

def main():
    try:
        TOKEN = "Your_Token"
        validator = EnhancedATHValidator(token=TOKEN)

        print("Running ATH quantum validation suite...")
        print("Note: This will run on quantum hardware and cost approximately $14.00")
        print("Available times: Mon-Wed 08:00-10:00 UTC, Thu-Fri 13:00-15:00 UTC")

        proceed = input("Do you want to proceed? (yes/no): ")
        if proceed.lower() != 'yes':
            print("Execution cancelled")
            return

        results = validator.run_enhanced_validation()
        
        if results:
            print("\nAnalyzing results...")
            analysis = validator.analyze_enhanced_results(results)
            
            print("\nEnhanced Validation Results:")
            print("===========================")
            
            for test_type, metrics in analysis.items():
                print(f"\n{test_type.replace('_', ' ').title()} Results:")
                print(f"Mean ± SEM: {metrics['mean']:.3f} ± {metrics['sem']:.3f}")
                print(f"R-squared: {metrics['r_squared']:.3f}")
                print(f"p-value: {metrics['p_value']:.3e}")
                print(f"Main Frequency: {metrics['main_frequency']:.3f}")
                if metrics['peaks']:
                    print(f"Peak Values: {', '.join([f'{p:.3f}' for p in metrics['peaks']])}")

            print("\nGenerating plots...")
            validator.plot_enhanced_results(results)
        else:
            print("No valid results to analyze")

    except Exception as e:
        print(f"Error during validation: {str(e)}")
        raise

if __name__ == "__main__":
    main()
