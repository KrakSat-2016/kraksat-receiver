#include <Python.h>
#include <math.h>

static const double G = 6.674e-11;
static const double R = 8.3144598;

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
    if(!PyArg_ParseTuple(args, "OOdd", &altitude_list, &acceleration_list,
                     &step, &max_radius))
        return NULL;

    if(!PyList_Check(altitude_list)) {
        PyErr_SetString(PyExc_TypeError, "altitude is not list");
        return NULL;
    }

    if(!PyList_Check(acceleration_list)) {
        PyErr_SetString(PyExc_TypeError, "acceleration is not list");
        return NULL;
    }

     if(PyList_Size(acceleration_list) != PyList_Size(altitude_list)) {
        PyErr_SetString(PyExc_TypeError,
            "acceleration have different length than altitude");
        return NULL;
    }

    for(double rad = step; rad < max_radius; rad += step) {
        double numerator = 0;
        for(int i = 0; i < (int)PyList_Size(altitude_list); i++) {
            PyObject *act_alti_obj = PyList_GetItem(altitude_list, i);
            PyObject *act_accel_obj = PyList_GetItem(acceleration_list, i);
            if(act_alti_obj == NULL || act_accel_obj == NULL)
                return NULL;
            double act_alti = PyFloat_AsDouble(act_alti_obj);
            double act_accel = PyFloat_AsDouble(act_accel_obj);
            if(PyErr_Occurred())
                return NULL;

            numerator += act_accel * square(rad + act_alti) / G;
        }

        double mass = numerator / (double)PyList_Size(altitude_list);
        double error = 0;

        for(int i = 0; i < (int)PyList_Size(altitude_list); i++) {
            PyObject *act_alti_obj = PyList_GetItem(altitude_list, i);
            PyObject *act_accel_obj = PyList_GetItem(acceleration_list, i);
            if(act_alti_obj == NULL || act_accel_obj == NULL)
                return NULL;
            double act_alti = PyFloat_AsDouble(act_alti_obj);
            double act_accel = PyFloat_AsDouble(act_accel_obj);
            if(PyErr_Occurred())
                return NULL;

            error += square(act_accel - G * mass / square(rad + act_alti));
        }

        if(error < res_error)
        {
            res_error = error;
            res_mass = mass;
            res_radius = rad;
        }
    }

    return Py_BuildValue("dd", res_radius, res_mass);
}

static PyObject *molar_mass(PyObject *self, PyObject *args)
{
    double temp, accel;
    PyObject *alti, *pres;

    if(!PyArg_ParseTuple(args, "ddOO", &temp, &accel, &alti, &pres))
        return NULL;

    if(!PyList_Check(alti)) {
        PyErr_SetString(PyExc_TypeError, "acceleration is not list");
        return NULL;
    }

    if(!PyList_Check(pres)) {
        PyErr_SetString(PyExc_TypeError, "pressure is not list");
        return NULL;
    }

    if(PyList_Size(alti) != PyList_Size(pres)) {
        PyErr_SetString(PyExc_TypeError,
            "acceleration have different length than pressure");
        return NULL;
    }

    double numerator = 0, denominator = 0;
    // const part of equation
    double con = R * temp / accel;

    for(int i = 0; i < PyList_Size(alti); ++i) {
        PyObject *pi_obj = PyList_GetItem(pres, i);
        PyObject * hi_obj = PyList_GetItem(alti, i);
        if(pi_obj == NULL || hi_obj == NULL)
            return NULL;

        double pi = PyFloat_AsDouble(pi_obj);
        double hi = PyFloat_AsDouble(hi_obj);
        if(PyErr_Occurred())
            return NULL;

        for(int j = i + 1; j < PyList_Size(alti); ++j) {
            PyObject *pj_obj = PyList_GetItem(pres, j);
            PyObject * hj_obj = PyList_GetItem(alti, j);
            if(pj_obj == NULL || hj_obj == NULL)
                return NULL;

            double pj = PyFloat_AsDouble(pj_obj);
            double hj = PyFloat_AsDouble(hj_obj);
            if(PyErr_Occurred())
                return NULL;

            numerator -= log(pj/pi);
            denominator += (hj - hi);
        }
    }

    return Py_BuildValue("d", con * numerator / denominator);
}

static char molar_mass_docstring[] =
    "Fallback method of molar mass computing. Use when ground pressure\n"
    "is unavailable.\n"
    "param temperature: mean temperature\n"
    "param acceleration: gravitational acceleration\n"
    "param altitude: list of altitude values\n"
    "param pressure: list of pressure values\n"
    "return: average molar_mass";

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
    {"molar_mass", molar_mass, METH_VARARGS, molar_mass_docstring},
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
