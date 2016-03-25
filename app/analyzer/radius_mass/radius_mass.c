#include <Python.h>

static const double G = 6.674e-11;

static inline double square(double a)
{
    return a * a;
}

static PyObject *radius_mass(PyObject *self, PyObject *args)
{
    double res_radius = 0, res_mass = 0, res_error = INFINITY;

    PyObject *altitude_list;
    PyObject *acceleration_list;
    double step, max_radius;
    if(!(PyArg_ParseTuple(args, "OOdd", &altitude_list, &acceleration_list,
                     &step, &max_radius)))
        return NULL;

    if(!PyList_Check(altitude_list) || !PyList_Check(altitude_list)) {
        PyErr_SetString(PyExc_TypeError, "list is required");
        goto error_exit;
    }

    if(PyList_Size(acceleration_list) != PyList_Size(altitude_list)) {
        PyErr_SetString(PyExc_TypeError, "lists have to be same length");
        goto error_exit;
    }


    for(double rad = step; rad < max_radius; rad += step) {
        double numerator = 0;
        for(int i = 0; i < (int)PyList_Size(altitude_list); i++) {
            PyObject *act_alti_obj = PyList_GetItem(altitude_list, i);
            PyObject *act_accel_obj = PyList_GetItem(acceleration_list, i);
            if(act_alti_obj == NULL || act_accel_obj == NULL)
                goto error_exit;
            double act_alti = PyFloat_AsDouble(act_alti_obj);
            double act_accel = PyFloat_AsDouble(act_accel_obj);
            if(PyErr_Occurred())
                goto error_exit;

            numerator += act_accel * square(rad + act_alti) / G;
        }

        double mass = numerator / (double)PyList_Size(altitude_list);
        double error = 0;

        for(int i = 0; i < (int)PyList_Size(altitude_list); i++) {
            PyObject *act_alti_obj = PyList_GetItem(altitude_list, i);
            PyObject *act_accel_obj = PyList_GetItem(acceleration_list, i);
            if(act_alti_obj == NULL || act_accel_obj == NULL)
                goto error_exit;
            double act_alti = PyFloat_AsDouble(act_alti_obj);
            double act_accel = PyFloat_AsDouble(act_accel_obj);
            if(PyErr_Occurred())
                goto error_exit;

            error += square(act_accel - G * mass / square(rad + act_alti));
        }

        if(error < res_error)
        {
            res_error = error;
            res_mass = mass;
            res_radius = rad;
        }
    }

    Py_DECREF(altitude_list);
    Py_DECREF(acceleration_list);
    return Py_BuildValue("dd", res_radius, res_mass);

    error_exit:
        Py_DECREF(altitude_list);
        Py_DECREF(acceleration_list);
        return NULL;
}

static char radius_mass_docstring[] =
    "Compute radius and mass\n"
    "param altitude: list of altitude values\n"
    "param acceleration: list of acceleration values\n"
    "param step: difference between two next tested radii\n"
    "param max_radius: maximal tested radius\n"
    "return: radius and mass\n"
    ":rtype: (float, float)";

static PyMethodDef module_methods[] = {
    {"radius_mass", radius_mass, METH_VARARGS, radius_mass_docstring},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef radius_massmodule = {
   PyModuleDef_HEAD_INIT,
   "radius_mass",
   "",
   -1,
   module_methods
};

PyMODINIT_FUNC PyInit_radius_mass(void)
{
    return PyModule_Create(&radius_massmodule);
}
