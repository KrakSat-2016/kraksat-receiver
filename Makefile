UI_DIR = app/ui
RESOURCE_DIR = app/ui/res
BUILD_DIR = app/ui
RADIUS_DIR = app/analyzer/radius_mass

UI_FILES = main.ui login.ui gsinfo.ui logs.ui parser.ui queue.ui statistics.ui missionstatus.ui
RESOURCES = res.qrc

PYUIC = pyuic5
PYRCC = pyrcc5
PYUICFLAGS = --from-imports
PYRCCFLAGS =

#################################

BUILT_UI = $(UI_FILES:%.ui=$(BUILD_DIR)/ui_%.py)
BUILT_RESOURCES = $(RESOURCES:%.qrc=$(BUILD_DIR)/%_rc.py)

all: resources ui radius

radius: $(RADIUS_DIR)/radius_mass.c
	python $(RADIUS_DIR)/setup.py build_ext --inplace
	rm -rf build
	mv *.so app/analyzer/

ui: $(BUILT_UI)
resources: $(BUILT_RESOURCES)

$(BUILD_DIR)/ui_%.py: $(UI_DIR)/%.ui
	$(PYUIC) $(PYUICFLAGS) -o $@ $<

$(BUILD_DIR)/%_rc.py: $(RESOURCE_DIR)/%.qrc
	$(PYRCC) $(PYRCCFLAGS) -o $@ $<

clean:
	$(RM) $(BUILT_UI) $(BUILT_RESOURCES) $(BUILT_UI:.py=.pyc) $(BUILT_RESOURCES:.py=.pyc)
