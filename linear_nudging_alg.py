from graphic_display import GraphicDisplay
# from matrix_nxn import Matrix_NxN # Not in use
from matrix_2x2 import Matrix_2x2
import matplotlib.pyplot as plt
import numpy as np
import datetime
import math
import time
import sys
import os

# 3D Stuff
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class LinearNudgingAlg:
    def __init__(self, *args):

        self._eigenvalue_magnitudes = []
        self._traces = []
        self._determinants = []
        self._nth_avg_abs_param_errors = []
        self._nth_avg_rel_param_errors = []
        self._ev_type = args[3]
        self._pp_type = args[4]
        self._param_list = args[5]
        n = str(args[0])
        n_x_n = n + 'x' + n

        if args[0] == len(args[5]) == 2:
            self._report_subdir = "../output/" + self._ev_type  + "_" + self._pp_type + "_"  + n_x_n + "/text_files/"
            self._report_filename = self._ev_type + "_" + self._pp_type + "_" + n_x_n + "_report"
        else:
            self._report_subdir = "../output/" + n_x_n + "/text_files/"
            self._report_filename = n_x_n + "_report"

        self._abs_graph_display = GraphicDisplay(args[0], args[2], "Absolute", self._ev_type, self._pp_type)
        self._rel_graph_display = GraphicDisplay(args[0], args[2], "Relative",  self._ev_type, self._pp_type)
        self.prepare_sim(args)


        if args[0] == len(args[5]) == 2:
            # self._abs_graph_display.plot_trace_det_graph(self._eigenvalue_magnitudes, self._nth_avg_abs_param_errors)
            self._abs_graph_display.plot_trace_det_graph(self._traces, self._determinants, self._nth_avg_abs_param_errors)
            self._abs_graph_display.plot_2D_ev_graph(self._eigenvalue_magnitudes, self._nth_avg_abs_param_errors)
            self._abs_graph_display.show_plot()

            self._rel_graph_display.plot_trace_det_graph(self._traces, self._determinants, self._nth_avg_rel_param_errors)
            self._rel_graph_display.plot_2D_ev_graph(self._eigenvalue_magnitudes, self._nth_avg_rel_param_errors)
            self._rel_graph_display.show_plot()

        # The code within this conditional should only work with 3 x 3 matricies.
        # if args[0] == len(args[5]) == 3:
        elif args[0] == len(args[5]) == 3:
            ########### EV Magnitudes
            self._abs_graph_display.plot_3D_ev_graph(self._eigenvalue_magnitudes, self._nth_avg_abs_param_errors)
            self._abs_graph_display.show_plot()

            self._rel_graph_display.plot_3D_ev_graph(self._eigenvalue_magnitudes, self._nth_avg_rel_param_errors)
            self._rel_graph_display.show_plot()

    def create_n_x_m_matrix_list(self, n, m):
        matrix = [[[] for j in range(m)] for i in range(n)]
        return matrix

    def get_eigenvalue_magnitude(self, A):
        src_eigenvals = np.linalg.eigvals(A)
        ev_magnitudes = []

        for i in range(len(src_eigenvals)):
            if isinstance(src_eigenvals[i], complex):
                ev_magnitudes.append(math.sqrt((src_eigenvals[i].real) ** 2 + (src_eigenvals[i].imag) ** 2))
            else:
                ev_magnitudes.append(src_eigenvals[i])
        return ev_magnitudes


    def get_param_error(self, est_param, true_param):
        return est_param - true_param

    def get_abs_param_error(self, est_param, true_param):
        return abs(self.get_param_error(est_param, true_param))

    def get_rel_param_error(self, est_param, true_param):
        return abs(self.get_param_error(est_param, true_param) / true_param)



    # def print_mtrx_stats(self, A):
    #     A.print_by_row()
    #     print("Eigenvalues:", A.get_eigenvalues(), "\n")
    #     print("Trace:", A.get_trace(), "\n")
    #     print("Determinant:", A.get_determinant(), "\n")

    def generate_matrix(self, n, bounds, ev_type, pp_type):
        # return np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]] )   # Manual option for testing
        if n == 2:
            A = Matrix_2x2(-bounds, bounds, ev_type, pp_type)
            return A.get_matrix()  # Extract the NumPy array from the Matrix_2x2 object
        else:
            return np.random.uniform(-bounds, bounds, (n, n))



    def prepare_sim(self, args):
        if len(args) == 6:
            n, bound_value, total_matricies, ev_type, pp_type = args[0], args[1], args[2], args[3], args[4]
            self.init_sim(n, bound_value, total_matricies, ev_type, pp_type)

    # def init_sim(self, n, bound_value, total_matricies, matrix_case_type):
    def init_sim(self, n, bound_value, total_matricies, ev_type, pp_type):
        sim_time = 10 # Stop time
        dt = 0.001    # Time step
        t_span = (0, sim_time)  # For solve_ivp (not used)
        t = np.arange(0, sim_time, dt) # Evaluation times
        T_R = 0.5        # Relaxation period
        init_param_err = bound_value * 2
        nudging_param_value = 1000
        Mu = np.eye(n) * nudging_param_value

        for i in range(total_matricies):
            self.custom_print("--------- MATRIX " + str(i) + " -------------------------------------------------------------", "\n")
            A = self.generate_matrix(n, bound_value, ev_type, pp_type)
            self.custom_print(f"A = {A} \n")
            self.custom_print(f"Eigenvalues = {np.linalg.eigvals(A)} \n")

            update_times_mtrx = np.empty((n, n), dtype = object)
            At = np.zeros((n, n), dtype = object)
            A_est = np.zeros((n, n), dtype = object)
            # Mu = np.eye(n) * nudging_param_value

            for j in range(n):
                for k in range(n):
                    update_times_mtrx[j, k] = np.array([0])

            # Add each element to the list
            for j in range(n):
                for k in range(n):
                    At[j, k] = A[j, k]
                    A_est[j, k] = np.array([At[j, k]])

            #Update the list based on the inputs
            for h in range(n):
                row, col = self.parse_matrix_parameter(self._param_list[h])
                for j in range(n):
                    for k in range(n):
                        if j == row and k == col:
                            At[j, k] = A[j, k] + init_param_err
                            A_est[j, k] = np.array([At[j, k]])

            S = np.zeros((1, n * 2))  # Each new solution point makes a new row
            U = np.zeros((1, n)) # Error terms: U = [u, v, w] = [xt - x, yt - y, zt - z] E.g. for 3 x 3 case
            U_rel = np.zeros((1, n))
            U_abs = np.zeros((1, n))
            for j in range(n * 2):
                if j < n:
                    S[0, j] = 1
                else:
                    S[0, j] = 3

            # Initialize system
            for j in range(n):
                U[0, j] = S[0, n + j] - S[0, j]
                U_abs[0, j] = abs(U[0, j])
                U_rel[0, j] = abs(U[0, j] / S[0, j])

            # if(n == 2):
            #     self._traces.append(A.get_trace(A))
            #     self._determinants.append(A.get_det(A))
            #     # self._traces.append(np.trace(A))
            #     # self._determinants.append(np.linalg.det(A))
            #
            # elif(n < 2):
            #     self._traces.append(np.trace(A))
            #     self._determinants.append(np.linalg.det(A))

            self._traces.append(np.trace(A))
            self._determinants.append(np.linalg.det(A))
            self._eigenvalue_magnitudes.append(self.get_eigenvalue_magnitude(A))

            self.nudge_alg(A, dt, t, T_R, update_times_mtrx, At, A_est, Mu, S, U, U_abs, U_rel, i)
            self.custom_print("\n")


    def parse_matrix_parameter(self, matrix_param):
        # Extracting the row and column indices from the input string
        row = int(matrix_param[1]) - 1
        col = int(matrix_param[2:]) - 1
        return row, col


    def F(self, t, A, S, At, Mu, U):
        """
        INPUT        t : time
        RETURNS  S_dot : right hand side of coupled reference + auxiliary system
        """
        n = A.shape[0] # Returns the number of rows of A
        X_dot = np.matmul(A, S[t, 0:n])
        Xt_dot = np.matmul(At, S[t, n:]) - np.matmul(Mu, U[t])
        S_dot = np.append(X_dot, Xt_dot)
        return S_dot

    def get_row_and_col_indicies(self, list, n):
        rows_indicies, cols_indicies = [], []
        for i in range(n):
            r, c = self.parse_matrix_parameter(self._param_list[i])
            rows_indicies.append(r)
            cols_indicies.append(c)
        return rows_indicies, cols_indicies


    def is_same_index(self, list):
        return all(i == list[0] for i in list)

    # def nudge_alg(self, A, dt, t, T_R, update_times_mtrx, At, A_est, Mu, S, U, U_rel, U_abs, matrix_id_number, matrix_case_type):
    def nudge_alg(self, A, dt, t, T_R, update_times_mtrx, At, A_est, Mu, S, U, U_rel, U_abs, matrix_id_number):
        n = A.shape[0]
        abs_param_err = [[] for _ in range(n)]
        rel_param_err = [[] for _ in range(n)]

        for i in range(n):
            j, k = self.parse_matrix_parameter(self._param_list[i])
            abs_param_err[i].append(self.get_abs_param_error(A_est[j, k][0], A[j, k]))
            rel_param_err[i].append(self.get_rel_param_error(A_est[j, k][0], A[j, k]))
        new_err_list = np.empty(n)
        new_err_list_abs = np.empty(n)
        new_err_list_rel = np.empty(n)


        for i in range(len(t) - 1):
            for h in range(n):
                j, k = self.parse_matrix_parameter(self._param_list[h])
                param_name = f'a{j + 1}{k + 1}'  # Construct the parameter name based on indices

                if param_name in self._param_list:
                    # print('index, j, k:', h,':' ,j, k)
                    if abs(U[i, j]) >= 0 and S[i, n + k] != 0 and t[i] - update_times_mtrx[j, k][-1] >= T_R:
                        At[j, k] = At[j, k] - Mu[k, k] * U[i, j] / S[i, n + k]
                        A_est[j, k] = np.append(A_est[j, k], At[j, k])
                        update_times_mtrx[j, k] = np.append(update_times_mtrx[j, k], t[i])
                    abs_param_err[h].append(self.get_abs_param_error(A_est[j, k][-1], A[j, k]))
                    rel_param_err[h].append(self.get_rel_param_error(A_est[j, k][-1], A[j, k]))

            # Integrate coupled reference and auxiliary system (forward Euler method)
            new_row = S[i] + self.F(i, A, S, At, Mu, U) * dt
            S = np.vstack((S, new_row))

            # Record new state error
            # print('ID,', 'g,',  'i,', 'elt:')
            for g in range(n):
                new_err_list[g] = S[i + 1, n + g] - S[i + 1, g]
                new_err_list_abs[g] = abs(new_err_list[g] )
                new_err_list_rel[g] = abs(new_err_list[g] / S[i + 1, g])
                # print( matrix_id_number,  g, i, new_err_list[g]) # For testing
                #self._state_error_matrix[matrix_id_number][g].append(new_err_list[g])
            # print("") - For printing

            # Record new state error
            U = np.vstack((U, new_err_list))
            U_abs = np.vstack((U_abs, new_err_list_abs))
            U_rel = np.vstack((U_rel, new_err_list_rel))
            # print("U", U, "")


        self._nth_avg_abs_param_errors.append(self.get_avg_of_list(abs_param_err))
        self._nth_avg_rel_param_errors.append(self.get_avg_of_list(rel_param_err))
        self.result_output(update_times_mtrx, A, A_est, t, S, U, U_abs, U_rel, abs_param_err, rel_param_err, matrix_id_number)


    def get_avg_of_list(self, my_list):
        sum = 0
        for i in range(len(my_list)):
            sum = my_list[i][-1] + sum
        return sum / len(my_list)


    def get_root_mean_square(self, double_list):
        num_rows = len(double_list)
        num_columns = len(double_list[0])  # Assuming all sublists have the same length
        rms_values = []

        for j in range(num_columns):
            squared_sum = 0
            for i in range(num_rows):
                squared_sum += double_list[i][j] ** 2
            rms = math.sqrt(squared_sum / num_rows)
            rms_values.append(rms)

        return rms_values


    def get_mean(self, double_list):
        num_rows = len(double_list)
        num_columns = len(double_list[0])  # Assuming all sublists have the same length
        mean_values = []

        for j in range(num_columns):
            column_sum = 0
            for i in range(num_rows):
                column_sum += double_list[i][j]
            mean = column_sum / num_rows
            mean_values.append(mean)
        return mean_values



    def custom_print(self, *args, **kwargs):
        # Print to the console
        print(*args, **kwargs)

        # Save to a text file
        subdir = self._report_subdir
        filename = self._report_filename
        os.makedirs(subdir, exist_ok = True)
        with open( subdir + filename + ".txt", "a") as output_file:  # Use "a" to append to the file
            original_stdout = sys.stdout
            sys.stdout = output_file
            print(*args, **kwargs)  # Write to the file
            sys.stdout = original_stdout  # Restore the original stdout





    def result_output(self, update_times_mtrx, A, A_est, t, S, U, U_abs, U_rel, abs_param_err, rel_param_err, matrix_id_number ):
        n = A.shape[0]
        self.custom_print(f"X = \n {S[:, 0:n]}\n")
        self.custom_print(f"Xt = \n {S[:, n:]}\n")
        self.custom_print(f"U_abs[-1] = {U_abs[-1]}\n") #Absolute Error
        self.custom_print(f"U_rel[-1] = {U_rel[-1]}\n") #Relative Error

        U_list = [[] for _ in range(n)]
        U_list_abs = [[] for _ in range(n)]
        U_list_rel = [[] for _ in range(n)]

        for i in range(len(U)):
            for j in range(n):
                U_list[j].append(U[i][j])
                U_list_abs[j].append(U_abs[i][j])
                U_list_rel[j].append(U_rel[i][j])

        # ABSOLUTE - RMS
        abs_state_err_rms = self.get_root_mean_square(U_list_abs)
        abs_param_err_rms = self.get_root_mean_square(abs_param_err)

        # RELATIVE - RMS
        rel_state_err_rms = self.get_root_mean_square(U_list_rel)
        rel_param_err_rms = self.get_root_mean_square(rel_param_err)


        # ABSOLUTE - MEAN
        abs_state_err_mean = self.get_mean(U_list_abs)
        abs_param_err_mean = self.get_mean(abs_param_err)

        # RELATIVE - MEAN
        rel_state_err_mean = self.get_mean(U_list_rel)
        rel_param_err_mean = self.get_mean(rel_param_err)


        # self._abs_graph_display.plot_2D_line_graph(t, U_list, matrix_id_number, "State Error")
        state_error_labels = [f'u{i + 1}' for i in range(len(U_list))]
        rms_graph_color_abs = mean_graph_color_abs = "blue"
        rms_graph_color_rel = mean_graph_color_rel = "red"


        # ABSOLUTE ERROR - SEPERATE
        self._abs_graph_display.plot_2D_line_graph(t, U_list_abs, matrix_id_number, state_error_labels, "absolute_error", "Absolute State Error", "N/A", "linear")
        self._abs_graph_display.plot_2D_line_graph(t, abs_param_err, matrix_id_number, self._param_list, "absolute_error", "Absolute Parameter Error", "N/A","linear")

        # RELATIVE ERROR - SEPERATE
        self._rel_graph_display.plot_2D_line_graph(t, U_list_rel, matrix_id_number, state_error_labels, "relative_error",  "Relative State Error", "N/A","linear")
        self._rel_graph_display.plot_2D_line_graph(t, rel_param_err, matrix_id_number, self._param_list, "relative_error", "Relative Parameter Error", "N/A","linear")



        # ABSOLUTE ERROR - RMS
        self._abs_graph_display.plot_2D_line_graph(t, [abs_state_err_rms], matrix_id_number,  ['Abs. State Err. (RMS)'], "absolute_error", "Absolute State Error RMS", rms_graph_color_abs, "linear")
        self._abs_graph_display.plot_2D_line_graph(t, [abs_param_err_rms], matrix_id_number, ['Abs. Param Err. (RMS)'], "absolute_error",  "Absolute Parameter Error RMS", rms_graph_color_abs, "linear")

        # RELATIVE ERROR - RMS
        self._rel_graph_display.plot_2D_line_graph(t, [rel_state_err_rms], matrix_id_number, ['Rel. State Err. (RMS)'], "relative_error", "Relative State Error RMS", rms_graph_color_rel, "linear")
        self._rel_graph_display.plot_2D_line_graph(t, [rel_param_err_rms], matrix_id_number, ['Rel. Param Err. (RMS)'], "relative_error", "Relative Parameter Error RMS", rms_graph_color_rel, "linear")



        # ABSOLUTE ERROR - MEAN
        self._abs_graph_display.plot_2D_line_graph(t, [abs_state_err_mean], matrix_id_number,  ['Abs. State Err. (MEAN)'], "absolute_error", "Absolute State Error MEAN", mean_graph_color_abs, "linear")
        self._abs_graph_display.plot_2D_line_graph(t, [abs_param_err_mean], matrix_id_number, ['Abs. Param Err. (MEAN)'], "absolute_error",  "Absolute Parameter Error MEAN", mean_graph_color_abs, "linear")

        # RELATIVE ERROR - MEAN
        self._rel_graph_display.plot_2D_line_graph(t, [rel_state_err_mean], matrix_id_number, ['Rel. State Err. (MEAN)'], "relative_error", "Relative State Error MEAN", mean_graph_color_rel, "linear")
        self._rel_graph_display.plot_2D_line_graph(t, [rel_param_err_mean], matrix_id_number, ['Rel. Param Err. (MEAN)'], "relative_error",  "Relative Parameter Error MEAN", mean_graph_color_rel, "linear")

        self.custom_print("matrix_id_number: ", matrix_id_number, 'trace:', self._traces[matrix_id_number], "det:", self._determinants[matrix_id_number])

        for i in range(n):
            j, k = self.parse_matrix_parameter(self._param_list[i])
            self.custom_print(f"{self._param_list[i]} = {A[j, k]}")
            self.custom_print(f"{self._param_list[i].title()}[-1] = {A_est[j, k][-1]}")
            self.custom_print(self._param_list[i], "Absolute Error:", abs_param_err[i][-1])
            self.custom_print(self._param_list[i], "Relative Error:", rel_param_err[i][-1])
            self.custom_print(f"{self._param_list[i].title()} = {A_est[j , k]}")
            self.custom_print("")
