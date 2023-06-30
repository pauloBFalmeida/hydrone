csv_filename = 'all_run.csv';
list_x = zeros(4);
for i = 1:4
  list_x(i) = list_x(i) + i;
end

fID = fopen(csv_filename,'w');

for i = 1:4
  fprintf(fID, '%f,', list_x(i));
end
fprintf(fID, '\n');
fclose(fID);


for i = 1:4
  list_x(i) = list_x(i) + i;
end

fID = fopen(csv_filename,'a');
  fprintf(fID, '%f,%f,%d,%d,\n', list_x(1), list_x(2), list_x(3), list_x(4));

fclose(fID);
