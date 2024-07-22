from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import io
import base64
import math

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        x_values = list(map(float, request.form.getlist('x_values')))
        y_values = list(map(float, request.form.getlist('y_values')))

        n = len(x_values)
        if n < 3:
            return render_template('index.html', error="Minimal tiga data titik diperlukan untuk perhitungan.")

        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_x2 = sum(x**2 for x in x_values)
        sum_y2 = sum(y**2 for y in y_values)
        sum_xy = sum(x*y for x, y in zip(x_values, y_values))

        b = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        a = (sum_y - b * sum_x) / n

        # Calculation of Δy²
        try:
            delta_y2 = (1 / (n - 2)) * (sum_y2 - (sum_x2 * (sum_y ** 2) - 2 * sum_x * sum_y * sum_xy + n * (sum_xy ** 2)) / (n * sum_x2 - (sum_x ** 2)))
        except ZeroDivisionError:
            return render_template('index.html', error="Terjadi pembagian dengan nol saat menghitung Δy².")

        # Correct calculation for Δb
        if delta_y2 < 0:
            return render_template('index.html', error="Δy² bernilai negatif, perhitungan tidak valid.")
        
        try:
            delta_b = math.sqrt(delta_y2 * n / (n * sum_x2 - sum_x**2))
        except ValueError:
            return render_template('index.html', error="Terjadi kesalahan domain matematika saat menghitung Δb.")

        delta_y = math.sqrt(delta_y2)

        pelaporan = f"{b:.15f}±{delta_b:.15f}"
        tk = (1 - delta_b / b) * 100

        equation = f"Y = {b:.2f}X + {a:.2f}"

        # Create the plot
        plt.figure()
        plt.plot(x_values, y_values, 'bo-', label='Data')
        plt.title('Grafik')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()

        # Save the plot to a PNG image
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        return render_template('index.html', x_values=x_values, y_values=y_values, sum_x=sum_x, sum_y=sum_y, sum_x2=sum_x2, sum_y2=sum_y2, sum_xy=sum_xy, b=b, delta_y2=delta_y2, delta_y=delta_y, delta_b=delta_b, pelaporan=pelaporan, tk=tk, equation=equation, image_base64=image_base64, n=n)
    except Exception as e:
        return render_template('index.html', error=f"Terjadi kesalahan: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
