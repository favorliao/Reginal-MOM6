       
 
close
clear all;
close all;

super_grid_file='/tigress/enhuil/regionalMOM_indianocean_new/grid2mif/supergrid_IndianOcean.nc';
depth_file='/tigress/enhuil/regionalMOM_indianocean_new/topog_IndianOceanbackup.nc';
mask_file='/tigress/enhuil/regionalMOM_indianocean_new/ocean_mask.nc';

h=ncread(depth_file,'depth')';
maskr=ncread(mask_file,'mask')';
lonx=ncread(super_grid_file,'x')';
laty=ncread(super_grid_file,'y')';

mifname=[super_grid_file(1:length(super_grid_file)-3)];
disp(strcat('Write mid mif files: ' ,mifname,'.mif'))
%writer_mifmid_regional_mom6(h,lonx,laty,maskr,mifname);

        
%function writer_mifmid_regional_mom6(h,lonx,laty,maskr,mifname) 
         [jm,im]=size(h);
         lon_c=lonx(1:2:end,1:2:end);
         lat_c=laty(1:2:end,1:2:end);

          namemif=[mifname,'.mif'];
          namemid=[mifname,'.mid'];
          
          miffile=fopen(namemif,'w+');                % Open file
          midfile=fopen(namemid,'w+');
          fprintf(miffile,'%c','VERSION 300');fprintf(miffile,'\n','');  
          fprintf(miffile,'%c','CHARSET "WINDOWSSIMPCHINESE"');fprintf(miffile,'\n',''); 
          fprintf(miffile,'%c','DELIMITER ","');fprintf(miffile,'\n','');   
          fprintf(miffile,'%c','CoordSys Earth Projection 1, 999, 3, 0, 0, 0');fprintf(miffile,'\n',''); 
          fprintf(miffile,'%c','COLUMNS 4');fprintf(miffile,'\n','');   
          fprintf(miffile,'%c','I integer');fprintf(miffile,'\n','');   
          fprintf(miffile,'%c','J integer');fprintf(miffile,'\n','');   
          fprintf(miffile,'%c','H float');fprintf(miffile,'\n','');   
          fprintf(miffile,'%c','FSM float');fprintf(miffile,'\n','');   
          fprintf(miffile,'%c','DATA');fprintf(miffile,'\n','');  
          fprintf(miffile,'%c',' ');fprintf(miffile,'\n','');  

          for j=2:jm+1
              if(mod(j,30)==0);disp([j,jm+1,j/(jm+1)]);end;
              for i=2:im+1
                  fprintf(miffile,'%c','Region 1');fprintf(miffile,'\n',''); 
                  fprintf(miffile,'%c','5');fprintf(miffile,'\n',''); 
                  fprintf(miffile,'%15.9f %15.9f',[lon_c(j-1,i-1), lat_c(j-1,i-1)]); fprintf(miffile,'\n',''); 
                  fprintf(miffile,'%15.9f %15.9f',[lon_c(j-1,i) ,lat_c(j-1,i)]); fprintf(miffile,'\n',''); 
                  fprintf(miffile,'%15.9f %15.9f',[lon_c(j,i) ,lat_c(j,i)]); fprintf(miffile,'\n',''); 
                  fprintf(miffile,'%15.9f %15.9f',[lon_c(j,i-1), lat_c(j,i-1)]);fprintf(miffile,'\n','');  
                  fprintf(miffile,'%15.9f %15.9f',[lon_c(j-1,i-1), lat_c(j-1,i-1)]);fprintf(miffile,'\n','');  
                  fprintf(miffile,'%c','Pen (1,2,0)'); fprintf(miffile,'\n',''); 
                  if maskr(j-1,i-1)~=1;
                      fprintf(miffile,'%c','Brush (1,0,16777215)');fprintf(miffile,'\n',''); 
                  end
                  if maskr(j-1,i-1)==1;
                      fprintf(miffile,'%c','Brush (2,12637695,16777215)');fprintf(miffile,'\n',''); 
                  end
                  fprintf(miffile,'%c','Center 0. 0.');fprintf(miffile,'\n',''); 
                  fprintf(midfile,'%i, %i, %f, %f\n',[i-1,j-1,h(j-1,i-1),maskr(j-1,i-1)]);
              end
          end
          fclose(miffile);
          fclose(midfile);

          disp(strcat('File written: ',namemif))
          disp(strcat('File written: ',namemid))
%end

