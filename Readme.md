# Steps to make the input files for regional MOM6

### 1. Make the supergrid.nc
supergrid.nc is the core file for model and it provides the grid point location (longitude and laitude) and resolution (dx and dy). Note that the supergrid.nc is 
not same with usual grid file like ROMS, POM. A detailed introduction of the grid file can be found [here](https://geoclim.princeton.edu/lrgroup/geoclim-mom6/wikis/MOM6-hgrid-file). A detailed file description can be found
[here](https://geoclim.princeton.edu/lrgroup/geoclim-mom6/wikis/MOM6-input-files-description). There are three steps to make the supergrid file.

* a. Use MOM6 preprocessing tools to directly make regional grid. The original link is in [GFDL github](https://github.com/NOAA-GFDL/MOM6-examples/tree/dev/gfdl/ice_ocean_SIS2/OM4_05/preprocessing). 
We are planning to use this tool, but haven't figure it out in detail. This do need some times.
* b. Use other tools (such as ROMS tools) to make roms grid. [CCS1](https://github.com/ESMG/ESMG-configs/tree/dev/esmg/CCS1/preprocessing) case use this option. The roms tools can be found in
[Kate's github](https://github.com/ESMG/pyroms) and other [link](http://romsagrif.gforge.inria.fr/)
* c. Use python to extract regional grid from global MOM6 grid. This option need to install MIDAS. The original link is in [Matt's github](https://github.com/mjharriso/MIDAS.git). 
After MIDAS installation, you can refer the extract code here (David, could you upload the code and build a subproject in the geoclim)

### 2. Make the mosaic, topography, mask, and other related files
This step need one tool: **fre_nctools**. The original link in is [GFDL github](https://github.com/NOAA-GFDL/FRE-NCtools). A Detailed installation guidance in Princeton 
cluster can be found here (David, could you build sub-project and give install guidance here?)

* a. In the princeton cluser, you need load module after installation to run the fre_nctools.
```
module purge
module load intel-mpi/intel/2018.3/64
module load intel/18.0/64/18.0.3.222
module load hdf5/intel-16.0/intel-mpi/1.8.16
module load netcdf/intel-16.0/hdf5-1.8.16/intel-mpi/4.4.0
```

* b. Use make_solo_mosaic to make mosaic name file. This step create only one file: ocean_IndianOcean.nc (you can rename the file here)
```
/tigress/GEOCLIM/LRGROUP/datasets/JRA55-do-v1.3merge/preprocessing/fre_nctools/build.fre-nctools.tiger1.rregrid.IMnSx/tools/make_solo_mosaic/make_solo_mosaic --num_tiles 1 --dir ./ --mosaic_name ocean_IndianOcean --tile_file supergrid_IndianOcean.nc
```

* c. Use make_quick_mosaic to make mask, topography and mosaic files. This step create six files: 
**grid_spec.nc land_mosaic_tile1Xocean_mosaic_tile1.nc atmos_mosaic_tile1Xocean_mosaic_tile1.nc atmos_mosaic_tile1Xland_mosaic_tile1.nc ocean_mask.nc land_mask.nc**
```
./make_quick_mosaic --input_mosaic ocean_IndianOcean.nc --mosaic_name grid_spec --ocean_topog topog_IndianOcean.nc
```
In addition, you can click [here](https://geoclim.princeton.edu/lrgroup/geoclim-mom6/wikis/MOM6-input-files-description) to get a detailed description of these files.

### 3. Make the open boundary files
The open boundary files are very important for the regional MOM6. The making tool is **PyCNAL**. The original link can be found in [ESMG github by Raf](https://github.com/ESMG/PyCNAL_regridding). 
In princeton cluster, you can found the installation guidance here (David, could you build the sub-project to provide guidance to install the PyCNAL and provide?)
You can use WOA, SODA, and global MOM6 data to create the boundary files. The boundary scheme in MOM6 can be found [here](https://github.com/NOAA-GFDL/MOM6-examples/wiki/Open-Boundary-Conditions).
The boundary file description can be found [here](https://geoclim.princeton.edu/lrgroup/geoclim-mom6/wikis/MOM6-input-files-description).

* a. Use WOA data to create boundary file. An example link can be found [here](https://github.com/ESMG/PyCNAL_regridding/tree/master/examples/WOA13). 
* b. Use global MOM6 results to create boundary file. An example link can be found [here](https://github.com/ESMG/PyCNAL_regridding/tree/master/examples/SODA3.3.1). 
* c. Use other global model data (e.g.SODA) to create boundary file. An example link can be found [here](https://github.com/ESMG/PyCNAL_regridding/tree/master/examples/MOM6). 

### 4. Set up the configuration of regional MOM6 in MOM_input
We need to tell the MOM6 that the boundary information and let the boundary file go into the model. An example of MOM_input configuration is here:
```
OBC_NUMBER_OF_SEGMENTS = 3      ! [Integer] The number of open boundary segments.
!OBC_SEGMENT_002 = "J=0,I=0:N,FLATHER,OBLIQUE,NUDGED"
!OBC_SEGMENT_001 = "J=N,I=N:0,FLATHER,OBLIQUE,NUDGED"
!OBC_SEGMENT_003 = "I=0,J=N:0,FLATHER,OBLIQUE,NUDGED"
OBC_SEGMENT_002 = "J=0,I=0:N,FLATHER,ORLANSKI,NUDGED,ORLANSKI_TAN,NUDGED_TAN"
OBC_SEGMENT_001 = "J=N,I=N:0,FLATHER,ORLANSKI,NUDGED,ORLANSKI_TAN,NUDGED_TAN"
OBC_SEGMENT_003 = "I=0,J=N:0,FLATHER,ORLANSKI,NUDGED,ORLANSKI_TAN,NUDGED_TAN"
OBC_SEGMENT_001_DATA = "U=file:obc_CCS1_1980-1990.nc(u),V=file:obc_CCS1_1980-1990.nc(v),SSH=file:obc_CCS1_1980-1990.nc(zeta),TEMP=file:obc_CCS1_1980-1990.nc(temp),SALT=file:obc_CCS1_1980-1990.nc(salt)"
OBC_SEGMENT_002_DATA = "U=file:obc_CCS1_1980-1990.nc(u),V=file:obc_CCS1_1980-1990.nc(v),SSH=file:obc_CCS1_1980-1990.nc(zeta),TEMP=file:obc_CCS1_1980-1990.nc(temp),SALT=file:obc_CCS1_1980-1990.nc(salt)"
OBC_SEGMENT_003_DATA = "U=file:obc_CCS1_1980-1990.nc(u),V=file:obc_CCS1_1980-1990.nc(v),SSH=file:obc_CCS1_1980-1990.nc(zeta),TEMP=file:obc_CCS1_1980-1990.nc(temp),SALT=file:obc_CCS1_1980-1990.nc(salt)"
OBC_SEGMENT_001_VELOCITY_NUDGING_TIMESCALES = 0.3, 360
OBC_SEGMENT_002_VELOCITY_NUDGING_TIMESCALES = 0.3, 360
OBC_SEGMENT_003_VELOCITY_NUDGING_TIMESCALES = 0.3, 360
OBC_TRACER_RESERVOIR_LENGTH_SCALE_OUT = 30000
OBC_TRACER_RESERVOIR_LENGTH_SCALE_IN = 3000
BRUSHCUTTER_MODE = True
OBC_FREESLIP_VORTICITY = False  !   [Boolean] default = True
OBC_COMPUTED_VORTICITY = True   !   [Boolean] default = False
                                ! If true, uses the external values of tangential velocity
                                ! in the relative vorticity on open boundaries. This cannot
                                ! be true if OBC_ZERO_VORTICITY or OBC_FREESLIP_VORTICITY is True.
OBC_FREESLIP_STRAIN = True      !   [Boolean] default = False
                                ! If true, sets the normal gradient of tangential velocity to
                                ! zero in the strain use in the stress tensor on open boundaries. This cannot
                                ! be true if OBC_ZERO_STRAIN is True.
OBC_ZERO_BIHARMONIC = True      !   [Boolean] default = False
                                ! If true, zeros the Laplacian of flow on open boundaries in the biharmonic
                                ! viscosity term.
```

