fileid = fclose('all');
fileid = fopen('S1_L2_T1.txt');
C1 = textscan(fileid,'%f %f %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s','Delimiter',',');
fileid = fclose('all');
t1 = C1{1,2}-C1{1,1};
g1 = C1{1,20};
fileid = fopen('S1_L2_T2.txt');
C2 = textscan(fileid,'%f %f %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s','Delimiter',',');
fileid = fclose('all');
t2 = C2{1,2}-C2{1,1};
g2 = C2{1,20};
fileid = fopen('S3_L2_T1.txt');
C3 = textscan(fileid,'%f %f %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s','Delimiter',',');
fileid = fclose('all');
t3 = C3{1,2}-C3{1,1};
g3 = C3{1,20};
fileid = fopen('S3_L2_T2.txt');
C4 = textscan(fileid,'%f %f %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s','Delimiter',',');
fileid = fclose('all');
t4 = C4{1,2}-C4{1,1};
g4 = C4{1,20};
fileid = fopen('S6_L2_T1.txt');
C5 = textscan(fileid,'%f %f %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s','Delimiter',',');
fileid = fclose('all');
t5 = C5{1,2}-C5{1,1};
g5 = C5{1,20};
fileid = fopen('S6_L2_T2.txt');
C6 = textscan(fileid,'%f %f %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s','Delimiter',',');
fileid = fclose('all');
t6 = C6{1,2}-C6{1,1};
g6 = C6{1,20};

times = vertcat(t1,t2,t3,t4,t5,t6);
gestures = vertcat(g1,g2,g3,g4,g5,g6);

cont1_0 = 0;cont1_1 = 0;cont1_2 = 0;cont2_0 = 0;cont2_1 = 0;cont2_2 = 0;cont3_0 = 0;
cont3_1 = 0;cont3_2 = 0;cont4_0 = 0;cont4_1 = 0;cont4_2 = 0;cont5_0 = 0;cont5_1 = 0;
cont5_2 = 0;cont5_3 = 0;cont5_4 = 0;cont6_0 = 0;cont6_1 = 0;cont6_2 = 0;cont6_3 = 0;
cont6_4 = 0;cont7_0 = 0;cont7_1 = 0;cont7_2 = 0;cont8_0 = 0;cont8_1 = 0;cont8_2 = 0;
cont9_0 = 0;cont9_1 = 0;cont9_2 = 0;cont10_0 = 0;cont10_1 = 0;cont10_2 = 0;
cont10_3 = 0;cont10_4 = 0;cont11_0 = 0;cont11_1 = 0;cont11_2 = 0;

for i = 1:size(times,1)
    x = gestures{i,1};
    e29 = '1_0';
    tf29 = strcmp(x,e29);
    if(tf29==1)
        cont1_0 = cont1_0 + 1;
        V1_0(cont1_0,1) = times(i,1);
    end
    e1 = '1_1';
    tf1 = strcmp(x,e1);
    if(tf1==1)
        cont1_1 = cont1_1 + 1;
        V1_1(cont1_1,1) = times(i,1);
    end
    e2 = '1_2';
    tf2 = strcmp(x,e2);
    if(tf2==1)
        cont1_2 = cont1_2 + 1;
        V1_2(cont1_2,1) = times(i,1);
    end
    e30 = '2_0';
    tf30 = strcmp(x,e30);
    if(tf30==1)
        cont2_0 = cont2_0 + 1;
        V2_0(cont2_0,1) = times(i,1);
    end
    e3 = '2_1';
    tf3 = strcmp(x,e3);
    if(tf3==1)
        cont2_1 = cont2_1 + 1;
        V2_1(cont2_1,1) = times(i,1);
    end
    e4 = '2_2';
    tf4 = strcmp(x,e4);
    if(tf4==1)
        cont2_2 = cont2_2 + 1;
        V2_2(cont2_2,1) = times(i,1);
    end
    e31 = '3_0';
    tf31 = strcmp(x,e31);
    if(tf31==1)
        cont3_0 = cont3_0 + 1;
        V3_0(cont3_0,1) = times(i,1);
    end
    e5 = '3_1';
    tf5 = strcmp(x,e5);
    if(tf5==1)
        cont3_1 = cont3_1 + 1;
        V3_1(cont3_1,1) = times(i,1);
    end
    e6 = '3_2';
    tf6 = strcmp(x,e6);
    if(tf6==1)
        cont3_2 = cont3_2 + 1;
        V3_2(cont3_2,1) = times(i,1);
    end
    e32 = '4_0';
    tf32 = strcmp(x,e32);
    if(tf32==1)
        cont4_0 = cont4_0 + 1;
        V4_0(cont4_0,1) = times(i,1);
    end
    e7 = '4_1';
    tf7 = strcmp(x,e7);
    if(tf7==1)
        cont4_1 = cont4_1 + 1;
        V4_1(cont4_1,1) = times(i,1);
    end
    e8 = '4_2';
    tf8 = strcmp(x,e8);
    if(tf8==1)
        cont4_2 = cont4_2 + 1;
        V4_2(cont4_2,1) = times(i,1);
    end
    e33 = '5_0';
    tf33 = strcmp(x,e33);
    if(tf33==1)
        cont5_0 = cont5_0 + 1;
        V5_0(cont5_0,1) = times(i,1);
    end
    e9 = '5_1';
    tf9 = strcmp(x,e9);
    if(tf9==1)
        cont5_1 = cont5_1 + 1;
        V5_1(cont5_1,1) = times(i,1);
    end
    e10 = '5_2';
    tf10 = strcmp(x,e10);
    if(tf10==1)
        cont5_2 = cont5_2 + 1;
        V5_2(cont5_2,1) = times(i,1);
    end
    e11 = '5_3';
    tf11 = strcmp(x,e11);
    if(tf11==1)
        cont5_3 = cont5_3 + 1;
        V5_3(cont5_3,1) = times(i,1);
    end
    e12 = '5_4';
    tf12 = strcmp(x,e12);
    if(tf12==1)
        cont5_4 = cont5_4 + 1;
        V5_4(cont5_4,1) = times(i,1);
    end
    e34 = '6_0';
    tf34 = strcmp(x,e34);
    if(tf34==1)
        cont6_0 = cont6_0 + 1;
        V6_0(cont6_0,1) = times(i,1);
    end
    e13 = '6_1';
    tf13 = strcmp(x,e13);
    if(tf13==1)
        cont6_1 = cont6_1 + 1;
        V6_1(cont6_1,1) = times(i,1);
    end
    e14 = '6_2';
    tf14 = strcmp(x,e14);
    if(tf14==1)
        cont6_2 = cont6_2 + 1;
        V6_2(cont6_2,1) = times(i,1);
    end
    e15 = '6_3';
    tf15 = strcmp(x,e15);
    if(tf15==1)
        cont6_3 = cont6_3 + 1;
        V6_3(cont6_3,1) = times(i,1);
    end
    e16 = '6_4';
    tf16 = strcmp(x,e16);
    if(tf16==1)
        cont6_4 = cont6_4 + 1;
        V6_4(cont6_4,1) = times(i,1);
    end
    e35 = '7_0';
    tf35 = strcmp(x,e35);
    if(tf35==1)
        cont7_0 = cont7_0 + 1;
        V7_0(cont7_0,1) = times(i,1);
    end
    e17 = '7_1';
    tf17 = strcmp(x,e17);
    if(tf17==1)
        cont7_1 = cont7_1 + 1;
        V7_1(cont7_1,1) = times(i,1);
    end
    e18 = '7_2';
    tf18 = strcmp(x,e18);
    if(tf18==1)
        cont7_2 = cont7_2 + 1;
        V7_2(cont7_2,1) = times(i,1);
    end
    e36 = '8_0';
    tf36 = strcmp(x,e36);
    if(tf36==1)
        cont8_0 = cont8_0 + 1;
        V8_0(cont8_0,1) = times(i,1);
    end
    e19 = '8_1';
    tf19 = strcmp(x,e19);
    if(tf19==1)
        cont8_1 = cont8_1 + 1;
        V7_1(cont8_1,1) = times(i,1);
    end
    e20 = '8_2';
    tf20 = strcmp(x,e20);
    if(tf20==1)
        cont8_2 = cont8_2 + 1;
        V8_2(cont8_2,1) = times(i,1);
    end
    e37 = '9_0';
    tf37 = strcmp(x,e37);
    if(tf37==1)
        cont9_0 = cont9_0 + 1;
        V9_0(cont9_0,1) = times(i,1);
    end
    e21 = '9_1';
    tf21 = strcmp(x,e21);
    if(tf21==1)
        cont9_1 = cont9_1 + 1;
        V9_1(cont9_1,1) = times(i,1);
    end
    e22 = '9_2';
    tf22 = strcmp(x,e22);
    if(tf22==1)
        cont9_2 = cont9_2 + 1;
        V9_2(cont9_2,1) = times(i,1);
    end
    e38 = '10_0';
    tf38 = strcmp(x,e38);
    if(tf38==1)
        cont10_0 = cont10_0 + 1;
        V10_0(cont10_0,1) = times(i,1);
    end
    e23 = '10_1';
    tf23 = strcmp(x,e23);
    if(tf23==1)
        cont10_1 = cont10_1 + 1;
        V10_1(cont10_1,1) = times(i,1);
    end
    e24 = '10_2';
    tf24 = strcmp(x,e24);
    if(tf24==1)
        cont10_2 = cont10_2 + 1;
        V10_2(cont10_2,1) = times(i,1);
    end
    e25 = '10_3';
    tf25 = strcmp(x,e25);
    if(tf25==1)
        cont10_3 = cont10_3 + 1;
        V10_3(cont10_3,1) = times(i,1);
    end
    e26 = '10_4';
    tf26 = strcmp(x,e26);
    if(tf26==1)
        cont10_4 = cont10_4 + 1;
        V6_4(cont10_4,1) = times(i,1);
    end
    e39 = '11_0';
    tf39 = strcmp(x,e39);
    if(tf39==1)
        cont11_0 = cont11_0 + 1;
        V11_0(cont11_0,1) = times(i,1);
    end
    e27 = '11_1';
    tf27 = strcmp(x,e27);
    if(tf27==1)
        cont11_1 = cont11_1 + 1;
        V11_1(cont11_1,1) = times(i,1);
    end
    e28 = '11_2';
    tf28 = strcmp(x,e28);
    if(tf28==1)
        cont11_2 = cont11_2 + 1;
        V11_2(cont11_2,1) = times(i,1);
    end
end
% mn1_0 = mean(V1_0);
% st1_0 = std(V1_0);
mn1_1 = mean(V1_1);
st1_1 = std(V1_1);
mn1_2 = mean(V1_2);
st1_2 = std(V1_2);
% mn2_0 = mean(V2_0);
% st2_0 = std(V2_0);
mn2_1 = mean(V2_1);
st2_1 = std(V2_1);
mn2_2 = mean(V2_2);
st2_2 = std(V2_2);
% mn3_0 = mean(V3_0);
% st3_0 = std(V3_0);
mn3_1 = mean(V3_1);
st3_1 = std(V3_1);
mn3_2 = mean(V3_2);
st3_2 = std(V3_2);
% mn4_0 = mean(V4_0);
% st4_0 = std(V4_0);
mn4_1 = mean(V4_1);
st4_1 = std(V4_1);
mn4_2 = mean(V4_2);
st4_2 = std(V4_2);
mn5_0 = mean(V5_0);
st5_0 = std(V5_0);
mn5_1 = mean(V5_1);
st5_1 = std(V5_1);
mn5_2 = mean(V5_2);
st5_2 = std(V5_2);
% mn5_3 = mean(V5_3);
% st5_3 = std(V5_3);
% mn5_4 = mean(V5_4);
% st5_4 = std(V5_4);
mn6_0 = mean(V6_0);
st6_0 = std(V6_0);
mn6_1 = mean(V6_1);
st6_1 = std(V6_1);
mn6_2 = mean(V6_2);
st6_2 = std(V6_2);
mn6_3 = mean(V6_3);
st6_3 = std(V6_3);
mn6_4 = mean(V6_4);
st6_4 = std(V6_4);
% mn7_0 = mean(V7_0);
% st7_0 = std(V7_0);
% mn7_1 = mean(V7_1);
% st7_1 = std(V7_1);
% mn7_2 = mean(V7_2);
% st7_2 = std(V7_2);
% mn8_0 = mean(V8_0);
% st8_0 = std(V8_0);
% mn8_1 = mean(V8_1);
% st8_1 = std(V8_1);
% mn8_2 = mean(V8_2);
% st8_2 = std(V8_2);
mn9_0 = mean(V9_0);
st9_0 = std(V9_0);
mn9_1 = mean(V9_1);
st9_1 = std(V9_1);
mn9_2 = mean(V9_2);
st9_2 = std(V9_2);
mn10_0 = mean(V10_0);
st10_0 = std(V10_0);
% mn10_1 = mean(V10_1);
% st10_1 = std(V10_1);
mn10_2 = mean(V10_2);
st10_2 = std(V10_2);
mn10_3 = mean(V10_3);
st10_3 = std(V10_3);
% mn10_4 = mean(V10_4);
% st10_4 = std(V10_4);
mn11_0 = mean(V11_0);
st11_0 = std(V11_0);
mn11_1 = mean(V11_1);
st11_1 = std(V11_1);
mn11_2 = mean(V11_2);
st11_2 = std(V11_2);