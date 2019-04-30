close
clear all;
close all;

modify_mid_file='/tigress/enhuil/regionalMOM_indianocean_new/grid2mif/supergrid_IndianOcean_modify.MID';
super_grid_file='/tigress/enhuil/regionalMOM_indianocean_new/grid2mif/supergrid_IndianOcean.nc';
depth_file='/tigress/enhuil/regionalMOM_indianocean_new/topog_IndianOceanbackup.nc';
mask_ocean_file='/tigress/enhuil/regionalMOM_indianocean_new/ocean_mask.nc';
mask_land_file='/tigress/enhuil/regionalMOM_indianocean_new/land_mask.nc';

h=ncread(depth_file,'depth')';
maskr=ncread(mask_ocean_file,'mask')';
hm_all=load(modify_mid_file);
[jm,im]=size(h);

num=0;tic;
for j=1:jm
    if mod(j,100)==0;toc;disp([j,jm,j/(jm)]);tic;end
    for i=1:im
        num=num+1;
        if i==hm_all(num,1) & j==hm_all(num,2);
           hnew(j,i)=hm_all(num,3);
           masknew(j,i)=hm_all(num,4);
        else
           error('i and j number is wrong! please check!');
        end
     end
end

hnew(masknew==0)=0;

modify_depth_file=[depth_file(1:length(depth_file)-3),'_modify.nc'];
modify_mask_ocean_file=[mask_ocean_file(1:length(mask_ocean_file)-3),'_modify.nc'];
modify_mask_land_file=[mask_land_file(1:length(mask_land_file)-3),'_modify.nc'];

copyfile(depth_file,modify_depth_file);
copyfile(mask_ocean_file,modify_mask_ocean_file);
copyfile(mask_land_file,modify_mask_land_file);

ncwrite(modify_depth_file,'depth',hnew');
ncwrite(modify_mask_ocean_file,'mask',masknew');
ncwrite(modify_mask_land_file,'mask',masknew');





