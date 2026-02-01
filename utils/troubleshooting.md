# Troubleshooting

## Numpy/Simplejpeg Compatibility Error

If you encounter the following error when using picamera2:

```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

This is caused by a version mismatch between numpy and simplejpeg. To fix it, run:

```bash
sudo pip3 install --upgrade --force-reinstall simplejpeg --break-system-packages
```

This will reinstall simplejpeg and recompile it against the current numpy version.
