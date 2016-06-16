"""description of changes

Revision ID: 5968a1fac1ed
Revises: 33bdcd4ac40e
Create Date: 2016-06-08 23:43:42.191324

"""

# revision identifiers, used by Alembic.
revision = '5968a1fac1ed'
down_revision = '33bdcd4ac40e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    ### end Alembic commands ###
    op.execute(sql='DROP TABLE norm CASCADE;')
    op.execute(sql='DROP TABLE norm_parameter CASCADE;')
    op.execute(sql='DROP TABLE norm_parameter_value CASCADE;')
    op.execute(sql='DROP TABLE norm_type CASCADE;')

    sql = """
INSERT INTO public.norm_furan (name, c1, c2, c3, c4) VALUES ('DOBLE', 100, 250, 250, 250);
INSERT INTO public.norm_furan (name, c1, c2, c3, c4) VALUES ('NONE/AUCUN', 0, 0, 0, 0);
    """
    op.execute(sql=sql)
    furan_sql = """
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('C57104', 1, 100, 120, 35, 50, 65, 350, 2500, 720, 0);
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('C57104', 2, 700, 400, 50, 100, 100, 570, 4000, 1920, 0);
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('C57104', 3, 1800, 1000, 80, 200, 150, 1400, 10000, 4630, 0);
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('C57104-R', 1, 100, 120, 35, 50, 65, 350, 2500, 720, 2);
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('C57104-R', 2, 700, 400, 50, 100, 100, 570, 4000, 1920, 2);
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('C57104-R', 3, 1800, 1000, 80, 200, 150, 1400, 10000, 4630, 2);
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('NONE/AUCUN', 1, 0, 0, 0, 0, 0, 0, 0, 0, 1);
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('NONE/AUCUN', 2, 0, 0, 0, 0, 0, 0, 0, 0, 1);
INSERT INTO public.norm_gas (name, condition, h2, ch4, c2h2, c2h4, c2h6, co, co2, tdcg, fluid_level) VALUES ('NONE/AUCUN', 3, 0, 0, 0, 0, 0, 0, 0, 0, 1);
    """

    op.execute(sql=furan_sql)

    isolation_sql = """
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (0, 32, 1.56, 1.57);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (1, 33.8, 1.54, 1.54);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (2, 35.6, 1.52, 1.5);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (3, 37.4, 1.5, 1.47);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (4, 39.2, 1.48, 1.44);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (5, 41, 1.46, 1.41);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (6, 42.8, 1.45, 1.37);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (7, 44.6, 1.44, 1.34);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (8, 46.4, 1.43, 1.31);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (9, 48.2, 1.41, 1.28);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (10, 50, 1.38, 1.25);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (11, 51.8, 1.35, 1.22);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (12, 53.6, 1.31, 1.19);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (13, 55.4, 1.27, 1.16);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (14, 57.2, 1.24, 1.14);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (15, 59, 1.2, 1.11);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (16, 60.8, 1.16, 1.09);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (17, 62.6, 1.12, 1.07);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (18, 64.4, 1.08, 1.05);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (19, 66.2, 1.04, 1.02);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (20, 68, 1, 1);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (21, 69.8, 0.96, 0.98);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (22, 71.6, 0.91, 0.96);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (23, 73.4, 0.87, 0.94);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (24, 75.2, 0.83, 0.92);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (25, 77, 0.79, 0.9);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (26, 78.8, 0.76, 0.88);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (27, 80.6, 0.73, 0.86);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (28, 82.4, 0.7, 0.84);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (29, 84.2, 0.67, 0.82);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (30, 86, 0.63, 0.8);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (31, 87.8, 0.6, 0.78);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (32, 89.6, 0.58, 0.76);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (33, 91.4, 0.56, 0.75);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (34, 93.2, 0.53, 0.73);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (35, 95, 0.51, 0.71);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (36, 96.8, 0.49, 0.7);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (37, 98.6, 0.47, 0.69);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (38, 100.4, 0.45, 0.67);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (39, 102.2, 0.44, 0.66);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (40, 104, 0.42, 0.65);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (41, 105.8, 0.4, 0.63);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (42, 107.6, 0.38, 0.62);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (43, 109.4, 0.37, 0.6);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (44, 111.2, 0.36, 0.59);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (45, 113, 0.34, 0.57);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (46, 114.8, 0.33, 0.56);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (47, 116.6, 0.31, 0.55);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (48, 118.4, 0.3, 0.54);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (49, 120.2, 0.29, 0.52);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (50, 122, 0.28, 0.51);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (52, 125.6, 0.26, 0.49);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (54, 129.2, 0.23, 0.47);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (56, 132.8, 0.21, 0.45);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (58, 136.4, 0.19, 0.43);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (60, 140, 0.17, 0.41);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (62, 143.6, 0.16, 0.4);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (64, 147.2, 0.15, 0.38);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (66, 150.8, 0.14, 0.36);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (68, 154.4, 0.13, 0.35);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (70, 158, 0.12, 0.33);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (72, 161.6, 0.12, 0.32);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (74, 165.2, 0.11, 0.31);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (76, 168.8, 0.1, 0.3);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (78, 172.4, 0.09, 0.28);
INSERT INTO public.norm_isolation (c, f, notseal, seal) VALUES (80, 176, 0.09, 0.27);

    """

    op.execute(sql=isolation_sql)

    physic_sql = """
INSERT INTO public.norm_physic (name, equipment_id, acid_min, acid_max, ift_min, ift_max, d1816_min, d1816_max, d877_min, d877_max, color_min, color_max, density_min, density_max, pf20_min, pf20_max, water_min, water_max, flashpoint_min, flashpoint_max, pourpoint_min, pourpoint_max, viscosity_min, viscosity_max, d1816_2_min, d1816_2_max, p100_min, p100_max, fluid_type_id, cei156_min, cei156_max) VALUES ('DEFAULT D', 4, 0, 0.4, 0, 0, 19, 24, 21, 25, 0, 0, 0, 0, 0, 0, 35, 50, 145, 145, -45, -45, 11, 11, 0, 0, null, null, 0, 0, 0);
INSERT INTO public.norm_physic (name, equipment_id, acid_min, acid_max, ift_min, ift_max, d1816_min, d1816_max, d877_min, d877_max, color_min, color_max, density_min, density_max, pf20_min, pf20_max, water_min, water_max, flashpoint_min, flashpoint_max, pourpoint_min, pourpoint_max, viscosity_min, viscosity_max, d1816_2_min, d1816_2_max, p100_min, p100_max, fluid_type_id, cei156_min, cei156_max) VALUES ('DEFAULT P', 11, 0, 0.4, 0, 0, 19, 24, 21, 25, 0, 0, 0, 0, 0, 0, 35, 50, 145, 145, -45, -45, 11, 11, 0, 0, null, null, 0, 0, 0);
INSERT INTO public.norm_physic (name, equipment_id, acid_min, acid_max, ift_min, ift_max, d1816_min, d1816_max, d877_min, d877_max, color_min, color_max, density_min, density_max, pf20_min, pf20_max, water_min, water_max, flashpoint_min, flashpoint_max, pourpoint_min, pourpoint_max, viscosity_min, viscosity_max, d1816_2_min, d1816_2_max, p100_min, p100_max, fluid_type_id, cei156_min, cei156_max) VALUES ('DEFAULT-H T', 14, 0.05, 0.1, 28, 32, 17, 20, 25, 29, 0, 3.5, 0.84, 0.906, 0.1, 0.3, 30, 34.9, 145, 145, -45, -45, 11, 11, 34, 40, 3, 4, 0, 0, 0);
INSERT INTO public.norm_physic (name, equipment_id, acid_min, acid_max, ift_min, ift_max, d1816_min, d1816_max, d877_min, d877_max, color_min, color_max, density_min, density_max, pf20_min, pf20_max, water_min, water_max, flashpoint_min, flashpoint_max, pourpoint_min, pourpoint_max, viscosity_min, viscosity_max, d1816_2_min, d1816_2_max, p100_min, p100_max, fluid_type_id, cei156_min, cei156_max) VALUES ('DEFAULT-R T', 14, 0.25, 0.25, 22, 28, 0, 0, 25, 29, 0, 3.5, 0.84, 0.906, 0.33, 1, 35, 50, null, 265, null, -20, null, 119, 34, 40, 3, 4, 2, 0, 0);
INSERT INTO public.norm_physic (name, equipment_id, acid_min, acid_max, ift_min, ift_max, d1816_min, d1816_max, d877_min, d877_max, color_min, color_max, density_min, density_max, pf20_min, pf20_max, water_min, water_max, flashpoint_min, flashpoint_max, pourpoint_min, pourpoint_max, viscosity_min, viscosity_max, d1816_2_min, d1816_2_max, p100_min, p100_max, fluid_type_id, cei156_min, cei156_max) VALUES ('DEFAULT-S T', 14, 10, 10, 0, 0, 0, 0, 25, 29, 1, 1, 0.95, 1.05, 0.1, 0.1, 50, 50, null, 340, null, 0, null, 50, 34, 40, 10, 10, 1, 0, 0);
    """

    op.execute(sql=physic_sql)

def downgrade():
    ### end Alembic commands ###
    op.execute(sql='TRUNCATE TABLE norm_furan CASCADE;')
    op.execute(sql='TRUNCATE TABLE norm_physic CASCADE;')
    op.execute(sql='TRUNCATE TABLE norm_isolation CASCADE;')
    op.execute(sql='TRUNCATE TABLE norm_gas CASCADE;')
