#!/usr/bin/env python
# Enhui Liao (enhuil@princeton.edu)
# this regrid only works for rectangular grid, not works for polar grid
import sys, os.path, os, datetime, glob
import xarray as xr, numpy as np, pandas as pd
#import matplotlib.pyplot as plt
import xesmf as xe
import drown

print()

#combined to one files which are from GFDL
fin = '/tigress/enhuil/regionalMOM6_tools/obc_initial_mking/res/global_mom6_025_ocean_monthly_z.2008_2018.allvars.nc'
fin_ssh = '/tigress/enhuil/regionalMOM6_tools/obc_initial_mking/res/global_mom6_025_ocean_monthly_z.2008_2018.allvars.nc'
#fin = '/tigress/GEOCLIM/LRGROUP/Liao/modelres/control_jra_variedpco2_2dpco2_afterspinup82yrs/hist_control_dynamics3d_hybrid_monthly__*.nc'
#fin_ssh = '/tigress/GEOCLIM/LRGROUP/Liao/modelres/control_jra_variedpco2_2dpco2_afterspinup82yrs/hist_control_dynamics2d_monthly__*.nc'
fin_grid = '/tigress/GEOCLIM/LRGROUP/Liao/modelres/control_jra_variedpco2_2dpco2_afterspinup82yrs/hist_control_ocean_static.nc'
fout_grid = '/tigress/enhuil/regionalMOM6_tools/grid_mask_mking/supergrid_IndianOcean.nc'
fout_mask = '/tigress/enhuil/regionalMOM6_tools/grid_mask_mking/ocean_mask_modify.nc'
fout = '/tigress/enhuil/regionalMOM6_tools/obc_initial_mking/res/obc_z_IndianOcean_from_global_mom6_025_2008_2018.nc'

#data_in = xr.open_mfdataset(fin,combine='by_coords',decode_times=False,decode_cf=False)
#data_in_ssh = xr.open_mfdataset(fin_ssh,combine='by_coords',decode_times=False,decode_cf=False)
data_in = xr.open_mfdataset(fin,combine='by_coords',decode_cf=False)
data_in_ssh = xr.open_mfdataset(fin_ssh,combine='by_coords',decode_cf=False)
grid_in = xr.open_dataset(fin_grid)
grid_out  = xr.open_dataset(fout_grid)
mask_out = xr.open_dataset(fout_mask)

#process obc grid and time information
#define the boundary, [east west south north], if it is open, then equal to 1, else 0; only works for four boundary
obc=[1,0,1,1]; sect_name=['east','west','south','north'];
#select boundary interpolation method from xesmf
method_interp='bilinear'; #['bilinear','conservative','patch','nearest_s2d','nearest_d2s']
#define the time range and lon lat range for obc files
#time_range=['1981-01-01','1983-01-01']; #for decode_time=true, but this takes lots of time to load data
tb=datetime.datetime(1958,1,1) #1900
time_range=[(datetime.datetime(2008,1,1)-tb).days, (datetime.datetime(2018,1,1)-tb).days];
lon_range=[grid_out.x.min()-2, grid_out.x.max()+2];#expand 2 degree for a safety
lat_range=[grid_out.y.min()-2, grid_out.y.max()+2];#expand 2 degree for a safety

time_bnds_bry=data_in.time_bnds.sel(time=slice(time_range[0],time_range[1]))

zc_name='z_l' #for z grid
# compute the layer thickness according to z_l (z depth of each layer)
exec(f'z_center=data_in.{zc_name}.values')
kmp1=len(z_center)+1
z_i=np.zeros((kmp1,1)) #z_i: z depth of interface layer
for k in range(kmp1):
    if k==0:
       z_i[0]=0 #should be ssh
    elif k==1:
       z_i[k]=z_i[k-1]+z_center[k-1]*2
    else:
       z_i[k]=z_i[k-1]+(z_center[k-1]-z_i[k-1])*2
dz=z_i[1:]-z_i[0:-1]

# cut region in global model results and do extrapolation in land and below bathmetry
# process temp, salt, u, v, h; h is for hybrid layer thickness
vout=['temp','salt','u','v']
inum=0
for v in ['thetao', 'so', 'uo', 'vo']:
    exec(f'da=data_in.{v}')
    if   v=='uo': da=da.rename({'xq':'lon','yh':'lat'});
    elif v=='vo': da=da.rename({'xh':'lon','yq':'lat'});
    else:         da=da.rename({'xh':'lon','yh':'lat'});
    #da.coords['lon'] = (da.coords['lon'] + 360) % 360;da = da.sortby(da.lon); #adjust lon from -300:60 to 0:360
    tstart = datetime.datetime.now();print('load and cut global model result...',v)
    da = da.sel(lon=slice(lon_range[0],lon_range[1]),lat=slice(lat_range[0],lat_range[1]),time=slice(time_range[0],time_range[1])).where(da !=1e20).load()
    print(datetime.datetime.now()-tstart)
    for l in range(len(da.time)):
        if np.mod(l,6)==0:
           print('variables=',v,' time_step=',l,'/',len(da.time));
           print(datetime.datetime.now()-tstart);tstart = datetime.datetime.now();
        exec(f'km=len(da.{zc_name})')
        for k in range(km):
            # adopt fortran function to do extrapolation in the land and below bathmetry, otherwise MOM6 can not run
            exec(f'tmpin=da.isel(time=l,{zc_name}=k).values.transpose()')
            #tmpin=da.isel(time=l,z_l=k).values.transpose()
            maskin =np.ones(tmpin.shape); maskin[np.where(np.isnan(tmpin))] = 0
            tmpmin = tmpin[np.where(maskin == 1)].min()
            tmpmax = tmpin[np.where(maskin == 1)].max()
            tmpnorm = ( tmpin - tmpmin) / (tmpmax - tmpmin)
            tmpnorm[np.where(np.isnan(tmpnorm))] = -99
            k_ew=-1; [ni, nj]=tmpnorm.shape # extrapolation coefficients
            tmpnorm_out = drown.drown(k_ew,tmpnorm,maskin,nb_inc=200,nb_smooth=40, ni=ni, nj=nj)
            tmpout = tmpmin + tmpnorm_out * (tmpmax - tmpmin)
            da.values[l,k,:,:]=tmpout.transpose()
    exec(f'{vout[inum]}_extra=da.copy()')
    inum=inum+1; del da

# process ssh data
da=data_in_ssh.zos.rename({'xh':'lon','yh':'lat'}) #zos is ssh name from GFDL files
da.coords['lon'] = (da.coords['lon'] + 360) % 360
da = da.sortby(da.lon)
da = da.sel(lon=slice(lon_range[0],lon_range[1]),lat=slice(lat_range[0],lat_range[1]),time=slice(time_range[0],time_range[1])).where(da !=1e20).load()
for l in range(len(da.time)):
    tmpin=da.isel(time=l).values.transpose()
    maskin =np.ones(tmpin.shape); maskin[np.where(np.isnan(tmpin))] = 0
    tmpin[np.where(np.isnan(tmpin))] = -99
    tmpmin = tmpin[np.where(maskin == 1)].min()
    tmpmax = tmpin[np.where(maskin == 1)].max()
    tmpnorm = ( tmpin - tmpmin) / (tmpmax - tmpmin)
    k_ew=-1; [ni, nj]=tmpnorm.shape # extrapolation coefficients
    tmpnorm_out = drown.drown(k_ew,tmpnorm,maskin,nb_inc=200,nb_smooth=40, ni=ni, nj=nj)
    tmpout = tmpmin + tmpnorm_out * (tmpmax - tmpmin)
    da.values[l,:,:]=tmpout.transpose()
ssh_extra=da.copy()+0.035 #0.035 is adjustment between zos and ssh; ssh_mean-zos_mean=0.035 in Indian Ocean area.
del da
# interpolate to the boundary of regional model
inum=0
for iobc in range(0,4):
    if obc[iobc] == 1:
       inum=inum+1
       if iobc == 0: print("computing east boundary ...");   grid_obc_out = xr.Dataset({'lat': (['lat'], grid_out.y[:,-1]), 'lon': (['lon'], grid_out.x[-2:-1,-1]) })
       if iobc == 1: print("computing west boundary ...");   grid_obc_out = xr.Dataset({'lat': (['lat'], grid_out.y[:,0]),  'lon': (['lon'], grid_out.x[0:1,0]) })
       if iobc == 2: print("computing south boundary ...");  grid_obc_out = xr.Dataset({'lat': (['lat'], grid_out.y[0,0:1]),'lon': (['lon'], grid_out.x[0,:]) })
       if iobc == 3: print("computing north boundary ...");  grid_obc_out = xr.Dataset({'lat': (['lat'], grid_out.y[-1,-2:-1]),'lon': (['lon'], grid_out.x[-1,:]) })

       # temp, salt, ssh, e(layer depth) are in the tracer point and can share the same regridder
       #regriddert = xe.Regridder(din_grid.rename({'geolon':'lon', 'geolat':'lat'}), grid_out, method=method_interp, periodic=True,reuse_weights=False)
       regriddert = xe.Regridder(temp_extra, grid_obc_out, method=method_interp, periodic=False)
       temp_bry = regriddert(temp_extra)
       salt_bry = regriddert(salt_extra)
       ssh_bry = regriddert(ssh_extra)
       #dz_bry = regriddert(h_extra)
       dz_bry = temp_bry.copy()
       exec(f'km=len(dz_bry.{zc_name})')
       for k in range(km):
           if k==0:
              dz_bry.data[:,k,:,:]=dz[k]+ssh_bry.data
           else:
              dz_bry.data[:,k,:,:]=dz[k]
       #mask might be needed here
       regriddert.clean_weight_file()

       #u and v source grid are not the same and can not share the same regridder
       regridderu = xe.Regridder(u_extra, grid_obc_out, method=method_interp, periodic=False)
       u_bry0 = regridderu(u_extra)
       regridderu.clean_weight_file()

       regridderv = xe.Regridder(v_extra, grid_obc_out, method=method_interp, periodic=False)
       v_bry0 = regridderv(v_extra)
       regridderv.clean_weight_file()

       #there is angle in the curvlinear grid
       da=grid_out.angle_dx.assign_coords(nyp=grid_out.y[:,0],nxp=grid_out.x[0,:])
       da=da.rename({'nxp':'lon','nyp':'lat'})
       u_bry=u_bry0*np.cos(da)+v_bry0*np.sin(da)
       v_bry=v_bry0*np.cos(da)-u_bry0*np.sin(da)

       #assign to different namie
       #encoding = {data_name: {'dtype': 'float32', 'zlib': True, 'complevel': 1}}
       lon_name=f'lon_segment_{inum:03d}'; lat_name=f'lat_segment_{inum:03d}'; dep_name=f'nz_segment_{inum:03d}';

       temp_name=f'temp_segment_{inum:03d}'; dz_temp_name='dz_'+temp_name;
       temp_bry=temp_bry.to_dataset(name=temp_name)
       temp_bry.attrs['long_name']=temp_name +'_'+ sect_name[iobc]
       temp_bry.attrs['units']='degree'
       dz_temp_bry=dz_bry.to_dataset(name=dz_temp_name)

       salt_name=f'salt_segment_{inum:03d}'; dz_salt_name='dz_'+salt_name;
       salt_bry=salt_bry.to_dataset(name=salt_name)
       salt_bry.attrs['long_name']=salt_name +'_'+ sect_name[iobc]
       salt_bry.attrs['units']='psu'
       dz_salt_bry=dz_bry.to_dataset(name=dz_salt_name)

       ssh_name=f'ssh_segment_{inum:03d}'
       ssh_bry=ssh_bry.to_dataset(name=ssh_name)
       ssh_bry.attrs['long_name']=ssh_name +'_'+ sect_name[iobc]
       ssh_bry.attrs['units']='m'

       u_name=f'u_segment_{inum:03d}'; dz_u_name='dz_'+u_name;
       u_bry=u_bry.to_dataset(name=u_name)
       u_bry.attrs['long_name']=u_name +'_'+ sect_name[iobc]
       u_bry.attrs['units']='m/s'
       dz_u_bry=dz_bry.to_dataset(name=dz_u_name)

       v_name=f'v_segment_{inum:03d}'; dz_v_name='dz_'+v_name;
       v_bry=v_bry.to_dataset(name=v_name)
       v_bry.attrs['long_name']=v_name +'_'+ sect_name[iobc]
       v_bry.attrs['units']='m/s'
       dz_v_bry=dz_bry.to_dataset(name=dz_v_name)
       
       dout_bry=xr.merge([temp_bry, dz_temp_bry, salt_bry, dz_salt_bry, ssh_bry, u_bry, dz_u_bry, v_bry, dz_v_bry,time_bnds_bry]).rename({'lon':lon_name,'lat':lat_name, zc_name:dep_name})
       encoding = {v:{'_FillValue': None, 'dtype': 'float32'}
          for v in [temp_name,salt_name,ssh_name,u_name,v_name,dz_temp_name,dz_salt_name,dz_u_name,dz_v_name,dep_name,lon_name,lat_name,'time']}
       if inum==1:
          dout_bry.to_netcdf(fout,mode='w',unlimited_dims=['time'], encoding=encoding)
       else:
          dout_bry.to_netcdf(fout,mode='a',unlimited_dims=['time'], encoding=encoding)


