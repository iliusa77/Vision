#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlalchemy as sqla
from app import db
from sqlalchemy.orm import relationship, relation
from sqlalchemy.sql.expression import cast
from sqlalchemy import Enum



def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


def get_class_by_tablename(tablename):
  """Return class reference mapped to table.

  :param tablename: String with name of table.
  :return: Class reference or None.
  """
  for c in db.Model._decl_class_registry.values():
    if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
      return c


class Lab(db.Model):
    __tablename__ = 'lab'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)
    analyser = db.Column(db.Unicode(256))
    name = db.Column(db.Unicode(256))

    # def __init__(self, code=0, name=''):
    #     self.code = code
    #     self.name = name

    def dump(self, _indent=0):
        return "   " * _indent + repr(self) + \
               "\n" + \
               "".join(
                   [c.dump(_indent + 1) for c in self.children.values()]
               )

    def __repr__(self):
        return self.name
        # return "Lab(id=%r, code=%r, name=%r)" % (
        #     self.id,
        #     self.code,
        #     self.name
        # )

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'code': self.code,
                'analyser': self.analyser,
                }


class ElectricalProfile(db.Model):
    __tablename__ = 'electrical_profile'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(256))
    description = db.Column(db.Unicode(1024))
    bushing = db.Column(db.Boolean(False))
    winding = db.Column(db.Boolean(False))
    insulation_pf = db.Column(db.Boolean(False))
    insulation = db.Column(db.Boolean(False))
    visual = db.Column(db.Boolean(False))
    resistance = db.Column(db.Boolean(False))
    degree = db.Column(db.Boolean(False))
    turns = db.Column(db.Boolean(False))

    def dump(self, _indent=0):
        return "   " * _indent + repr(self) + \
               "\n" + \
               "".join(
                   [c.dump(_indent + 1) for c in self.children.values()]
               )

    # def parsedata(self, data):
    #     if data:
    #         for key in data.keys():
    #             # print key + ' ' + data[key]
    #             if hasattr(self, key):
    #                 if key == 'selection' or key == 'description':
    #                     if data[key]:
    #                         setattr(self, key, data[key])
    #                 else:
    #                     setattr(self, key, True if data[key] == 'y' else False)
    #
    # def __init__(self, data=None):
    #     self.parsedata(data)
    #     # print getattr(self, key)

    def clear_data(self):
        for attr in self.__dict__:
            if attr in ['id', '_sa_instance_state']:
                continue
            # print attr
            value = '' if attr in ('name', 'description') else False
            setattr(self, attr, value)

    def add_data(self, data):
        self.parsedata(data)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                'bushing': self.bushing,
                'winding': self.winding,
                'insulation_pf': self.insulation_pf,
                'insulation': self.insulation,
                'visual': self.visual,
                'resistance': self.resistance,
                'degree': self.degree,
                'turns': self.turns,
                'profile_type': 'electrical_profile',
                }


class ContractStatus(db.Model):
    __tablename__ = 'contract_status'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), index=True)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class SamplingPoint(db.Model):
    __tablename__ = 'sampling_point'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), index=True)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class Contract(db.Model):
    __tablename__ = 'contract'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), index=True)
    code = db.Column(db.String(50), index=True)
    # user 1 enters manually
    # ContractNum: What is the contract number within the company
    # ContractStatus: What is the status of the contract
    contract_status_id = db.Column(
        'contract_status_id',
        db.ForeignKey("contract_status.id"),
        nullable=False
    )
    contract_status = relationship(ContractStatus, backref="contract")

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'code': self.code,
                'contract_status_id': self.contract_status_id,
                'contract_status': self.contract_status and self.contract_status.serialize()
                }


class SamplingCard(db.Model):
    __tablename__ = 'sampling_card'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    # SamplingcardPrint: Indicate if the sampling cart need to be printed to fill in the field information
    # user 2 has to print small form
    card_print = db.Column(db.Boolean)
    # SamplingCardGathered: Used for printing the card in batch
    card_gathered = db.Column(db.Integer)

    def __repr__(self):
        return self.id

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'card_gathered': self.sampling_card_gathered,
                'card_print': self.sampling_card_print,
                }


class Campaign(db.Model):
    """
    Campaign: Contain current analysis results, who did it and why. It also contain analysis management and statuses
    If a test is done on the equipment, then an Analysis record is created
    """
    __tablename__ = u'campaign'

    # __table_args__ = (
    # will be reviewed
    # db.Index(u'campaign_DatePrelevement_NoEquipement_NoSerieEquipe_TypeAnal_key', u'DatePrelevement', u'NoEquipement', u'NoSerieEquipe', u'TypeAnalyse', u'ClefAnalyse', unique=True),
    # db.Index(u'campaign_NoEquipement_NoSerieEquipe_DatePrelevement_ClefAnal_key', u'NoEquipement', u'NoSerieEquipe', u'DatePrelevement', u'ClefAnalyse', u'TypeAnalyse', unique=True),
    # db.Index(u'campaign_SerieDate', u'NoSerieEquipe', u'DatePrelevement', u'ClefAnalyse', u'TypeAnalyse'),
    # db.Index(u'campaign_TypeAnalyse_NoEquipement_NoSerieEquipe_DatePrelevem_key', u'TypeAnalyse', u'NoEquipement', u'NoSerieEquipe', u'DatePrelevement', u'ClefAnalyse', unique=True),
    # db.Index(u'campaign_NoEquipement_NoSerieEquipe_TypeAnalyse_DatePrelevem_key', u'NoEquipement', u'NoSerieEquipe', u'TypeAnalyse', u'DatePrelevement', u'ClefAnalyse', unique=True),
    # db.Index(u'campaign_DateSerie', u'DatePrelevement', u'NoSerieEquipe', u'TypeAnalyse', u'ClefAnalyse'),
    # db.Index(u'campaign_Condition_douteuse', u'NoEquipement', u'NoSerieEquipe', u'If_OK', u'DatePrelevement'),
    # db.Index(u'campaign_NoEquipement', u'NoEquipement', u'NoSerieEquipe')
    # )

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    date_created = db.Column(db.DateTime, index=True) # date of campaign start
    created_by_id = db.Column(db.ForeignKey("users_user.id"), nullable=False)
    created_by = db.relationship('User', foreign_keys='Campaign.created_by_id')
    contract_id = db.Column(db.ForeignKey("contract.id"), nullable=True)
    contract = db.relationship('Contract', foreign_keys='Campaign.contract_id')
    date_sampling = db.Column(db.DateTime, index=True)
    description = db.Column(db.Text)
    status_id = db.Column(db.ForeignKey("campaign_status.id"), nullable=True)
    status = db.relationship('CampaignStatus', foreign_keys='Campaign.status_id')

    #
    # # Bolean field that may no longer be required
    # if_rem = db.Column(db.String(5))
    # # Bolean field that may no longer be required
    # if_ok = db.Column(db.String(5))

    # data_valid = db.Column(db.Integer, server_default=db.text("0"), nullable=True)  # DataValid: Need to look into
    # status1 = db.Column(db.Integer, server_default=db.text("0"), nullable=True)  # Status1: Need to look into
    # status2 = db.Column(db.Integer, server_default=db.text("0"), nullable=True)  # Status2:	 Need to look into
    # error_state = db.Column(db.Integer, server_default=db.text("0"), nullable=True)  # ErrorState: Need to look into
    # error_code = db.Column(db.Integer, server_default=db.text("0"), nullable=True)  # ErrorCode: Need to look into

    # TODO equipment_id as a property (SQLAlchemy query filter doesn't use this property in comparison)
    @property
    def equipment_id(self):
        class MyList(object):
            def __init__(self, *args):
                self.my_list = args

            def __eq__(self, other):
                return other in self.my_list

        return MyList([x.equipment_id for x in db.session.query(TestResult).filter_by(campaign_id=id)])

    def __repr__(self):
        return 'Campaign {0}, created at {1} by {2}'.format(self.id, self.date_created, self.created_by)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'date_created': dump_datetime(self.date_created),
            'date_sampling': dump_datetime(self.date_sampling),
            'created_by_id': self.created_by_id,
            'created_by': self.created_by and self.created_by.serialize(),
            'contract_id': self.contract_id,
            'contract': self.contract and self.contract.serialize(),
            'status_id': self.status_id,
            'status': self.status and self.status.serialize(),
            'description': self.description,

            # 'if_rem': self.if_rem,
            # 'if_ok': self.if_ok,
            # 'date_application': self.date_application,


            # 'data_valid': self.data_valid,
            # 'status1': self.status1,
            # 'status2': self.status2,
            # 'error_state': self.error_state,
            # 'error_code': self.error_code,


            'test_result': [ res.serialize() for res in db.session.query(TestResult).filter_by(campaign_id=self.id)]
        }


class FluidProfile(db.Model):
    __tablename__ = 'fluid_profile'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Unicode(256))
    description = db.Column(db.Unicode(1024))

    # syringe
    gas = db.Column(db.Boolean(False))
    water = db.Column(db.Boolean(False))
    furans = db.Column(db.Boolean(False))
    inhibitor = db.Column(db.Boolean(False))
    pcb = db.Column(db.Boolean(False))
    qty = db.Column(db.Integer) # qty Syringe
    sampling = db.Column(db.Integer)
    # jar
    dielec = db.Column(db.Boolean(False))
    acidity = db.Column(db.Boolean(False))
    density = db.Column(db.Boolean(False))
    pcb_jar = db.Column(db.Boolean(False))
    inhibitor_jar = db.Column(db.Boolean(False))
    point = db.Column(db.Boolean(False))
    dielec_2 = db.Column(db.Boolean(False))
    color = db.Column(db.Boolean(False))
    pf = db.Column(db.Boolean(False))
    particles = db.Column(db.Boolean(False))
    metals = db.Column(db.Boolean(False))
    viscosity = db.Column(db.Boolean(False))
    dielec_d = db.Column(db.Boolean(False))
    ift = db.Column(db.Boolean(False))
    pf_100 = db.Column(db.Boolean(False))
    furans_f = db.Column(db.Boolean(False))
    water_w = db.Column(db.Boolean(False))
    corr = db.Column(db.Boolean(False))
    dielec_i = db.Column(db.Boolean(False))
    visual = db.Column(db.Boolean(False))
    qty_jar = db.Column(db.Integer)
    sampling_jar = db.Column(db.Integer)
    # vial
    pcb_vial = db.Column(db.Boolean(False))
    antioxidant = db.Column(db.Boolean(False))
    qty_vial = db.Column(db.Integer)
    sampling_vial = db.Column(db.Integer)

    # def parsedata(self, data):
    #     if data:
    #         for key in data.keys():
    #             if hasattr(self, key):
    #                 if key in ['selection', 'description', 'qty', 'sampling', 'qty_jar', 'sampling_jar', 'qty_vial',
    #                            'sampling_vial', 'sampling_vial']:
    #                     if data[key]:
    #                         setattr(self, key, data[key])
    #                 else:
    #                     setattr(self, key, True if data[key] == 'y' else False)
    #
    # def __init__(self, data=None):
    #     self.parsedata(data)

    def clear_data(self):
        for attr in self.__dict__:
            if attr in ['id', '_sa_instance_state']:
                continue
            # print attr
            if attr in ('name', 'description'):
                setattr(self, attr, '')
            if attr in ['qty', 'sampling', 'qty_jar', 'sampling_jar', 'qty_vial', 'sampling_vial', 'sampling_vial']:
                setattr(self, attr, 0)
            else:
                setattr(self, attr, False)

    def add_data(self, data):
        self.parsedata(data)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                'gas': self.gas,
                'water': self.water,
                'furans': self.furans,
                'inhibitor': self.inhibitor,
                'pcb': self.pcb,
                'qty': self.qty,
                'sampling': self.sampling,
                'dielec': self.dielec,
                'acidity': self.acidity,
                'density': self.density,
                'pcb_jar': self.pcb_jar,
                'inhibitor_jar': self.inhibitor_jar,
                'point': self.point,
                'dielec_2': self.dielec_2,
                'color': self.color,
                'pf': self.pf,
                'particles': self.particles,
                'metals': self.metals,
                'viscosity': self.viscosity,
                'dielec_d': self.dielec_d,
                'ift': self.ift,
                'pf_100': self.pf_100,
                'furans_f': self.furans_f,
                'water_w': self.water_w,
                'corr': self.corr,
                'dielec_i': self.dielec_i,
                'visual': self.visual,
                'qty_jar': self.qty_jar,
                'sampling_jar': self.sampling_jar,
                'pcb_vial': self.pcb_vial,
                'antioxidant': self.antioxidant,
                'qty_vial': self.qty_vial,
                'sampling_vial': self.sampling_vial,
                'profile_type': 'fluid_profile',
                }


class EquipmentType(db.Model):
    __tablename__ = u'equipment_type'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    code = db.Column(db.String(50))
    table_name = db.Column(db.String(50))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'code': self.code,
                'table_name': self.table_name,
                }


class Material(db.Model):
    __tablename__ = u'material'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    code = db.Column(db.String(50))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'code': self.code
                }


class FluidType(db.Model):
    __tablename__ = u'fluid_type'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class Location(db.Model):
    # PhyPosition GPS location
    __tablename__ = u'location'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    # Site. What is the name of the site.
    # Example. A company may have a assembly plants in several cities,
    # therefore each site is named after each city where the plant is.
    name = db.Column(db.String(50), index=True)  # should be relation

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class Manufacturer(db.Model):
    __tablename__ = u'manufacturer'


    # def __init__(self, code=0, name=''):
    #     self.code = code
    #     self.name = name

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    markings = db.Column(db.UnicodeText)
    location = db.Column(db.Unicode(256))
    description = db.Column(db.UnicodeText)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'markings': self.markings,
                'location': self.location,
                'description': self.description,
                }


class GasSensor(db.Model):
    """
    GasSensor. List gas sensor with their respective sensitivity to each measured gas
     """
    __tablename__ = u'gas_sensor'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))  # Sensor. Sensor commercial name
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    model = db.Column(db.String(50))

    h2 = db.Column(db.Float(53), server_default=db.text("0"))  # Remaining are equivalent
    ch4 = db.Column(db.Float(53), server_default=db.text("0"))
    c2h2 = db.Column(db.Float(53), server_default=db.text("0"))
    c2h4 = db.Column(db.Float(53), server_default=db.text("0"))
    c2h6 = db.Column(db.Float(53), server_default=db.text("0"))
    co = db.Column(db.Float(53), server_default=db.text("0"))
    co2 = db.Column(db.Float(53), server_default=db.text("0"))
    o2 = db.Column(db.Float(53), server_default=db.text("0"))
    n2 = db.Column(db.Float(53), server_default=db.text("0"))

    # ppmError. Calculated ppm error by comparing lab ppm from sample with sensor reading at sampling time
    ppm_error = db.Column(db.Integer, server_default=db.text("0"))

    # percentError. Calculated error in percent
    percent_error = db.Column(db.Float(53), server_default=db.text("0"))

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'model': self.model,
                'h2': self.h2,
                'ch4': self.ch4,
                'c2h2': self.c2h2,
                'c2h4': self.c2h4,
                'c2h6': self.c2h6,
                'co': self.co,
                'co2': self.co2,
                'o2': self.o2,
                'n2': self.n2,
                'ppm_error': self.ppm_error,
                'percent_error': self.percent_error,
                }


class Transformer(db.Model):
    __tablename__ = u'transformer'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    # FluidVolume. Quantity of insulating fluid in equipment in litre
    fluid_volume = db.Column(db.Float)
    sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    welded_cover = db.Column(db.Boolean)
    windings = db.Column(db.Integer)  # Windings. Number of windings in transformer
    cooling_rating = db.Column(db.Integer)
    autotransformer = db.Column(db.Boolean)  # Autotransformer. True if it is
    threephase = db.Column(db.Boolean)

    # FluidType. Insulating fluid used in equipment
    fluid_type_id = db.Column('fluid_type_id', db.ForeignKey("fluid_type.id"), nullable=False)
    fluid_type = relationship('FluidType', backref='transformer')

    fluid_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))
    fluid_level = db.relationship('FluidLevel', foreign_keys='Transformer.fluid_level_id')

    gassensor_id = db.Column('gas_sensor_id', db.ForeignKey("gas_sensor.id"), nullable=False)
    gas_sensor = relationship('GasSensor', backref='transformer')

    phase_number = db.Column(db.Enum('1', '3', '6', name="Phase number"))  # PhaseNum. 1=single phase, 3=triphase, 6=hexaphase
    frequency = db.Column(db.Enum('25', '50', '60', 'DC', name="Frequency"), default=db.text('25'))  # frequency. Operating frequency


    primary_tension = db.Column(db.Float(53))  # Volt1. Primary voltage in kV
    secondary_tension = db.Column(db.Float(53))  # Volt2. Secondary voltage in kV
    tertiary_tension = db.Column(db.Float(53))  # Volt3. Tertiary voltage in kV

    based_transformerp_ower = db.Column(db.Float(53))  # MVA1. Based transformer power
    first_cooling_stage_power = db.Column(db.Float(53))  # MVA2. First cooling stage power
    second_cooling_stage_power = db.Column(db.Float(53))  # MVA3. second cooling stage power



    # is a separate device
    # PrimConnection. Primary windings connection on a multi phase transformer
    primary_winding_connection = db.Column(db.Integer)
    # SecConnection. Secondary windings connection on a multi phase transformer
    secondary_winding_connection = db.Column(db.Integer)
    # TertConnection. Tertiary windings connection on a multi phase transformer
    tertiary_winding_connection = db.Column(db.Integer)

    # winding metal is a property of winding
    windind_metal = db.Column(db.Integer)  # WindingMetal. Copper or aluminium

    bil1 = db.Column(db.Float(53))  # BIL1. Primary Insulation level in kV
    bil2 = db.Column(db.Float(53))  # BIL2. Secondary Insulation level in kV
    bil3 = db.Column(db.Float(53))  # BIL3. Tertiary Insulation level in kV

    static_shield1 = db.Column(db.Boolean)  # StaticShield1. true with primary electrostatic shield is present
    static_shield2 = db.Column(db.Boolean)  # StaticShield2. true with secondary electrostatic shield is present
    static_shield3 = db.Column(db.Boolean)  # StaticShield3. true with tertiary electrostatic shield is present

    # it's transformer property
    bushing_neutral1 = db.Column(db.Float(53))
    bushing_neutral2 = db.Column(db.Float(53))
    bushing_neutral3 = db.Column(db.Float(53))
    bushing_neutral4 = db.Column(db.Float(53))

    ltc1 = db.Column(db.Float(53))  # LTC1.
    ltc2 = db.Column(db.Float(53))  # LTC2
    ltc3 = db.Column(db.Float(53))  # LTC3

    temperature_rise = db.Column(db.Integer)  # TemperatureRise. Transformer temperature rise

    # it can be a property and also can be tested
    impedance1 = db.Column(db.Float(53))  # Impedance1. Impedance at base MVA
    imp_base1 = db.Column(db.Float(53))  # ImpBasedMVA1

    impedance2 = db.Column(db.Float(53))  # Impedance2. Impedance at first forced cooling MVA
    imp_base2 = db.Column(db.Float(53))  # ImpBasedMVA2

    mvaforced11 = db.Column(db.Float(53))  # MVAForced11
    mvaforced12 = db.Column(db.Float(53))  # MVAForced12
    mvaforced13 = db.Column(db.Float(53))  # MVAForced13
    mvaforced14 = db.Column(db.Float(53))  # MVAForced14
    mvaforced21 = db.Column(db.Float(53))  # MVAForced21
    mvaforced22 = db.Column(db.Float(53))  # MVAForced22
    mvaforced23 = db.Column(db.Float(53))  # MVAForced23
    mvaforced24 = db.Column(db.Float(53))  # MVAForced24

    impedance3 = db.Column(db.Float(53))  # Impedance3. Impedance at third forced cooling MVA
    impbasedmva3 = db.Column(db.Float(53))  # ImpBasedMVA3

    # it belongs to transformer , tap voltage, it s a part of the test process
    formula_ratio2 = db.Column(db.Integer)  # RatioFormula2. Formula used for TTR

    # it belongs to transformer , tap voltage, it s a part of the test process
    formula_ratio = db.Column(db.Integer)  # RatioFormula. Formula used for TTR
    ratio_tag1 = db.Column(db.String(20))  # RatioTag1. Tag use for TTR
    ratio_tag2 = db.Column(db.String(20))  # RatioTag2. Tag use for TTR
    ratio_tag3 = db.Column(db.String(20))  # RatioTag3. Tag use for TTR
    ratio_tag4 = db.Column(db.String(20))  # RatioTag4. Tag use for TTR
    ratio_tag5 = db.Column(db.String(20))  # RatioTag5. Tag use for TTR
    ratio_tag6 = db.Column(db.String(20))  # RatioTag6. Tag use for TTR

    bushing_serial1_id = db.Column(
        'bushing_serial1',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial1 = relationship('Bushing', foreign_keys="Transformer.bushing_serial1_id")

    bushing_serial2_id = db.Column(
        'bushing_serial2',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial2 = relationship('Bushing', foreign_keys="Transformer.bushing_serial2_id")

    bushing_serial3_id = db.Column(
        'bushing_serial3',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial3 = relationship('Bushing', foreign_keys="Transformer.bushing_serial3_id")

    bushing_serial4_id = db.Column(
        'bushing_serial4',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial4 = relationship('Bushing', foreign_keys="Transformer.bushing_serial4_id")

    bushing_serial5_id = db.Column(
        'bushing_serial5',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial5 = relationship('Bushing', foreign_keys="Transformer.bushing_serial5_id")

    bushing_serial6_id = db.Column(
        'bushing_serial6',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial6 = relationship('Bushing', foreign_keys="Transformer.bushing_serial6_id")

    bushing_serial7_id = db.Column(
        'bushing_serial7',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial7 = relationship('Bushing', foreign_keys="Transformer.bushing_serial7_id")

    bushing_serial8_id = db.Column(
        'bushing_serial8',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial8 = relationship('Bushing', foreign_keys="Transformer.bushing_serial8_id")

    bushing_serial9_id = db.Column(
        'bushing_serial9',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial9 = relationship('Bushing', foreign_keys="Transformer.bushing_serial9_id")

    bushing_serial10_id = db.Column(
        'bushing_serial10',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial10 = relationship('Bushing', foreign_keys="Transformer.bushing_serial10_id")

    bushing_serial11_id = db.Column(
        'bushing_serial11',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial11 = relationship('Bushing', foreign_keys="Transformer.bushing_serial11_id")

    bushing_serial12_id = db.Column(
        'bushing_serial12',
        db.ForeignKey("bushing.id"),
        nullable=True
    )
    bushing_serial12 = relationship('Bushing', foreign_keys="Transformer.bushing_serial12_id")

    # device property ,  for  transformer
    mvaactual = db.Column(db.Float(53))  # MVAActual. Actual MVA used
    mvaractual = db.Column(db.Float(53))  # MVARActual. Actual MVA used
    mwreserve = db.Column(db.Float(53))  # MWReserve. How much MW in reserve for backup
    mvarreserve = db.Column(db.Float(53))  # MVARReserve. How much MVAR in reserve for backup
    mwultime = db.Column(db.Float(53))  # MWUltima. How much MW can ultimately be used in emergency
    mvarultime = db.Column(db.Float(53))  # MVARUltima. How much MVAR can ultimately be used in emergency

    # transformer device property
    mva4 = db.Column(db.Float(53))  # MVA4

    # it transformer property
    # QuatConnection. Quaternary windings connection on a multi phase transformer
    quaternary_winding_connection = db.Column(db.Float(53))

    # tranformer property
    bil4 = db.Column(db.Float(53))  # BIL4. Tertiary Insulation level in kV
    # tranformer property
    static_shield4 = db.Column(db.Float(53))  # StaticShield4. true with tertiary electrostatic shield is present

    # tranformer property
    ratio_tag7 = db.Column(db.Float(53))  # RatioTag7. Tag use for TTR
    ratiot_ag8 = db.Column(db.Float(53))  # RatioTag8. Tag use for TTR
    formula_ratio3 = db.Column(db.Float(53))  # RatioFormula3

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'fluid_volume': self.fluid_volume,
                'sealed': self.sealed,
                'welded_cover': self.welded_cover,
                'windings': self.windings,
                'cooling_rating': self.cooling_rating,
                'autotransformer': self.autotransformer,
                'threephase': self.threephase,
                'fluid_type_id': self.fluid_type_id,
                'fluid_type': self.fluid_type and self.fluid_type.serialize(),
                'fluid_level_id': self.fluid_level_id,
                'fluid_level': self.fluid_level and self.fluid_level.serialize(),
                'gassensor_id': self.gassensor_id,
                'gas_sensor': self.gas_sensor and self.gas_sensor.serialize(),
                'phase_number': self.phase_number,
                'frequency': self.frequency,
                'primary_tension': self.primary_tension,
                'secondary_tension': self.secondary_tension,
                'tertiary_tension': self.tertiary_tension,
                'based_transformerp_ower': self.based_transformerp_ower,
                'first_cooling_stage_power': self.first_cooling_stage_power,
                'second_cooling_stage_power': self.second_cooling_stage_power,
                'primary_winding_connection': self.primary_winding_connection,
                'secondary_winding_connection': self.secondary_winding_connection,
                'tertiary_winding_connection': self.tertiary_winding_connection,
                'windind_metal': self.windind_metal,
                'bil1': self.bil1,
                'bil2': self.bil2,
                'bil3': self.bil3,
                'static_shield1': self.static_shield1,
                'static_shield2': self.static_shield2,
                'static_shield3': self.static_shield3,
                'bushing_neutral1': self.bushing_neutral1,
                'bushing_neutral2': self.bushing_neutral2,
                'bushing_neutral3': self.bushing_neutral3,
                'bushing_neutral4': self.bushing_neutral4,
                'ltc1': self.ltc1,
                'ltc2': self.ltc2,
                'ltc3': self.ltc3,
                'temperature_rise': self.temperature_rise,
                'impedance1': self.impedance1,
                'imp_base1': self.imp_base1,
                'impedance2': self.impedance2,
                'imp_base2': self.imp_base2,
                'mvaforced11': self.mvaforced11,
                'mvaforced12': self.mvaforced12,
                'mvaforced13': self.mvaforced13,
                'mvaforced14': self.mvaforced14,
                'mvaforced21': self.mvaforced21,
                'mvaforced22': self.mvaforced22,
                'mvaforced23': self.mvaforced23,
                'mvaforced24': self.mvaforced24,
                'impedance3': self.impedance3,
                'impbasedmva3': self.impbasedmva3,
                'formula_ratio2': self.formula_ratio2,
                'formula_ratio': self.formula_ratio,
                'ratio_tag1': self.ratio_tag1,
                'ratio_tag2': self.ratio_tag2,
                'ratio_tag3': self.ratio_tag3,
                'ratio_tag4': self.ratio_tag4,
                'ratio_tag5': self.ratio_tag5,
                'ratio_tag6': self.ratio_tag6,
                'bushing_serial1_id': self.bushing_serial1_id,
                'bushing_serial1': self.bushing_serial1 and self.bushing_serial1.serialize(),
                'bushing_serial2_id': self.bushing_serial2_id,
                'bushing_serial2': self.bushing_serial2 and self.bushing_serial2.serialize(),
                'bushing_serial3_id': self.bushing_serial3_id,
                'bushing_serial3': self.bushing_serial3 and self.bushing_serial3.serialize(),
                'bushing_serial4_id': self.bushing_serial4_id,
                'bushing_serial4': self.bushing_serial4 and self.bushing_serial4.serialize(),
                'bushing_serial5_id': self.bushing_serial5_id,
                'bushing_serial5': self.bushing_serial5 and self.bushing_serial5.serialize(),
                'bushing_serial6_id': self.bushing_serial6_id,
                'bushing_serial6': self.bushing_serial6 and self.bushing_serial6.serialize(),
                'bushing_serial7_id': self.bushing_serial7_id,
                'bushing_serial7': self.bushing_serial7 and self.bushing_serial7.serialize(),
                'bushing_serial8_id': self.bushing_serial8_id,
                'bushing_serial8': self.bushing_serial8 and self.bushing_serial8.serialize(),
                'bushing_serial9_id': self.bushing_serial9_id,
                'bushing_serial9': self.bushing_serial9 and self.bushing_serial9.serialize(),
                'bushing_serial10_id': self.bushing_serial10_id,
                'bushing_serial10': self.bushing_serial10 and self.bushing_serial10.serialize(),
                'bushing_serial11_id': self.bushing_serial11_id,
                'bushing_serial11': self.bushing_serial11 and self.bushing_serial11.serialize(),
                'bushing_serial12_id': self.bushing_serial12_id,
                'bushing_serial12': self.bushing_serial12 and self.bushing_serial12.serialize(),
                'mvaactual': self.mvaactual,
                'mvaractual': self.mvaractual,
                'mwreserve': self.mwreserve,
                'mvarreserve': self.mvarreserve,
                'mwultime': self.mwultime,
                'mvarultime': self.mvarultime,
                'mva4': self.mva4,
                'quaternary_winding_connection': self.quaternary_winding_connection,
                'bil4': self.bil4,
                'static_shield4': self.static_shield4,
                'ratio_tag7': self.ratio_tag7,
                'ratiot_ag8': self.ratiot_ag8,
                'formula_ratio3': self.formula_ratio3,
                }


class Breaker(db.Model):
    __tablename__ = u'breaker'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    current_rating = db.Column(db.Numeric(6))
    open = db.Column(db.Boolean, default=True)

    fluid_type_id = db.Column('fluid_type_id', db.ForeignKey("fluid_type.id"), nullable=True)
    fluid_type = db.relationship('FluidType', foreign_keys='Breaker.fluid_type_id')

    fluid_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))
    fluid_level = db.relationship('FluidLevel', foreign_keys='Breaker.fluid_level_id')

    interrupting_medium_id = db.Column(db.Integer, db.ForeignKey("interrupting_medium.id"))
    interrupting_medium = db.relationship('InterruptingMedium', foreign_keys='Breaker.interrupting_medium_id')

    breaker_mechanism_id = db.Column(db.Integer, db.ForeignKey("breaker_mechanism.id"))
    breaker_mechanism = db.relationship('BreakerMechanism', foreign_keys='Breaker.breaker_mechanism_id')
    # phase_number = db.Column(sqla.Enum('1', '3', '6', name="Phase number"))  # PhaseNum. 1=single phase, 3=triphase, 6=hexaphase
    # frequency = db.Column(sqla.Enum('25', '50', '60', 'DC', name="Frequency"), default=db.text('25'))  # frequency. Operating frequency
    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    # # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    # welded_cover = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'current_rating': self.current_rating,
                'open': self.open,
                'fluid_type_id': self.fluid_type_id,
                'fluid_type': self.fluid_type and self.fluid_type.serialize(),
                'fluid_level_id': self.fluid_level_id,
                'fluid_level': self.fluid_level and self.fluid_level.serialize(),
                'interrupting_medium_id': self.interrupting_medium_id,
                'interrupting_medium': self.interrupting_medium and self.interrupting_medium.serialize(),
                'breaker_mechanism_id': self.breaker_mechanism_id,
                'breaker_mechanism': self.breaker_mechanism and self.breaker_mechanism.serialize(),
                }


class LoadTapChanger(db.Model):
    __tablename__ = u'tap_changer'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)

    # Filter. What condition is the filter. We must make this field a selection choice such Good, bad, replace etc..
    filter = db.Column(db.String(30))
    counter = db.Column(db.Integer)  # Counter. Used for load tap changer or arrester (ligthning)
    number_of_taps = db.Column(db.Integer)
    model = db.Column(db.String(50))

    # relatons
    fluid_type_id = db.Column('fluid_type_id', db.ForeignKey("fluid_type.id"), nullable=True)
    fluid_type = db.relationship('FluidType', foreign_keys='LoadTapChanger.fluid_type_id')

    fluid_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))
    fluid_level = db.relationship('FluidLevel', foreign_keys='LoadTapChanger.fluid_level_id')

    interrupting_medium_id = db.Column(db.Integer, db.ForeignKey("interrupting_medium.id"))
    interrupting_medium = db.relationship('InterruptingMedium', foreign_keys='LoadTapChanger.interrupting_medium_id')

    # phase_number = db.Column(sqla.Enum('1', '3', '6', name="Phase number"))  # PhaseNum. 1=single phase, 3=triphase, 6=hexaphase
    # frequency = db.Column(sqla.Enum('25', '50', '60', 'DC', name="Frequency"), default=db.text('25'))  # frequency. Operating frequency
    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    # # description = db.Column(db.UnicodeText)
    # # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    # welded_cover = db.Column(db.Boolean)
    # # tap changer property property
    # ltc4 = db.Column(db.Float(53))  # LTC4

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'filter': self.filter,
                'counter': self.counter,
                'number_of_taps': self.number_of_taps,
                'model': self.model,
                'fluid_type_id': self.fluid_type_id,
                'fluid_type': self.fluid_type and self.fluid_type.serialize(),
                'fluid_level_id': self.fluid_level_id,
                'fluid_level': self.fluid_level and self.fluid_level.serialize(),
                'interrupting_medium_id': self.interrupting_medium_id,
                'interrupting_medium': self.interrupting_medium and self.interrupting_medium.serialize(),
                }


class Bushing(db.Model):
    __tablename__ = u'bushing'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    type = ['phase', 'Neutral']
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    model = db.Column(db.String(50))
    kv = db.Column(db.Float)  # voltage
    sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    current = db.Column(db.Integer)
    fluid_volume = db.Column(db.Float)
    bil = db.Column(db.Numeric(8))
    c1 = db.Column(db.Float)
    c1pf = db.Column(db.Float)
    c2 = db.Column(db.Float)
    c2pf = db.Column(db.Float)

    fluid_type_id = db.Column('fluid_type_id', db.ForeignKey("fluid_type.id"), nullable=True)
    fluid_type = db.relationship('FluidType', foreign_keys='Bushing.fluid_type_id')
    # #
    # # # PhaseNum. 1=single phase, 3=triphase, 6=hexaphase
    # # phase_number = db.Column(sqla.Enum('1', '3', '6', name="Phase number"))
    # #
    # # # frequency. Operating frequency
    # # frequency = db.Column(sqla.Enum('25', '50', '60', 'DC', name="Frequency"), default=db.text('25'))
    # # description = db.Column(sqla.UnicodeText())  # description. Describe the equipment function
    # winding = db.Column(db.Integer, nullable=False)  # Winding. Winding, primary, secondary, etc. been measured
    # bushing_manufacturer_h1 = db.Column(db.String(25))  # Bushing manufacturer for H1
    # bushing_manufacturer_h2 = db.Column(db.String(25))  # Bushing manufacturer for H2
    # bushing_manufacturer_h3 = db.Column(db.String(25))  # Bushing manufacturer for H3
    # bushing_manufacturer_hn = db.Column(db.String(25))  # Bushing manufacturer for HN
    # bushing_manufacturer_x1 = db.Column(db.String(25))  # Bushing manufacturer for X1
    # bushing_manufacturer_x2 = db.Column(db.String(25))  # Bushing manufacturer for X2
    # bushing_manufacturer_x3 = db.Column(db.String(25))  # Bushing manufacturer for X3
    # bushing_manufacturer_xn = db.Column(db.String(25))  # Bushing manufacturer for XN
    # bushing_manufacturer_t1 = db.Column(db.String(25))  # Bushing manufacturer for T1
    # bushing_manufacturer_t2 = db.Column(db.String(25))  # Bushing manufacturer for T2
    # bushing_manufacturer_t3 = db.Column(db.String(25))  # Bushing manufacturer for T3
    # bushing_manufacturer_tn = db.Column(db.String(25))  # Bushing manufacturer for TN
    # bushing_manufacturer_q1 = db.Column(db.String(25))  # Bushing manufacturer for Q1
    # bushing_manufacturer_q2 = db.Column(db.String(25))  # Bushing manufacturer for Q2
    # bushing_manufacturer_q3 = db.Column(db.String(25))  # Bushing manufacturer for Q3
    # bushing_manufacturer_qn = db.Column(db.String(25))  # Bushing manufacturer for QN
    # bushing_type_h = db.Column(db.String(25))  # Bushing type for H
    # bushing_type_hn = db.Column(db.String(25))  # Bushing type for HN
    # bushing_type_x = db.Column(db.String(25))  # Bushing type for X
    # bushing_type_xn = db.Column(db.String(25))  # Bushing type for XN
    # bushing_type_t = db.Column(db.String(25))  # Bushing type for T
    # bushing_type_tn = db.Column(db.String(25))  # Bushing type for TN
    # bushing_type_q = db.Column(db.String(25))  # Bushing type for Q
    # bushing_type_qn = db.Column(db.String(25))  # Bushing type for QN

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'type': self.type,
                'name': self.name,
                'serial': self.serial,
                'model': self.model,
                'kv': self.kv,
                'sealed': self.sealed,
                'current': self.current,
                'fluid_volume': self.fluid_volume,
                'bil': self.bil,
                'c1': self.c1,
                'c1pf': self.c1pf,
                'c2': self.c2,
                'c2pf': self.c2pf,
                'fluid_type_id': self.fluid_type_id,
                'fluid_type': self.fluid_type and self.fluid_type.serialize(),
                }


class EquipmentConnection(db.Model):
    __tablename__ = u'equipment_connection'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    equipment_id = db.Column('equipment_id', db.ForeignKey("equipment.id"))
    equipment = db.relationship('Equipment', foreign_keys='EquipmentConnection.equipment_id')
    parent_id = db.Column('parent_id', db.ForeignKey("equipment.id"))
    parent = db.relationship('Equipment', foreign_keys='EquipmentConnection.parent_id')

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'equipment_id': self.equipment_id,
                'equipment': self.equipment and self.equipment.serialize(),
                'parent_id': self.parent_id,
                'parent': self.parent and self.parent.serialize(),
                }


class NeutralResistance(db.Model):
    __tablename__ = u'resistance'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)

    # its a separate device should be splitted into another table
    neutral_resistance = db.Column(db.Float(53))  # NeutralResistance1.
    neutral_resistance1 = db.Column(db.Float(53))  # NeutralResistance1.
    neutral_resistance0 = db.Column(db.Boolean)  # NeutralResistance0
    neutral_resistance2 = db.Column(db.Float(53))  # NeutralResistance2
    neutral_resistance3 = db.Column(db.Float(53))  # NeutralResistance3

    # it's status or mode  of a resistance
    neutral_resistance_open1 = db.Column(db.Boolean)  # NeutralResistanceOpen1
    neutral_resistance_open2 = db.Column(db.Boolean)  # NeutralResistanceOpen2
    # property of resistence, it's status
    neutral_resistance_open3 = db.Column(db.Float(53))  # NeutralResistanceOpen3
    kv = db.Column(db.Float)  # voltage
    bil = db.Column(db.Numeric(8))
    open = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'neutral_resistance': self.neutral_resistance,
                'neutral_resistance1': self.neutral_resistance1,
                'neutral_resistance0': self.neutral_resistance0,
                'neutral_resistance2': self.neutral_resistance2,
                'neutral_resistance3': self.neutral_resistance3,
                'neutral_resistance_open1': self.neutral_resistance_open1,
                'neutral_resistance_open2': self.neutral_resistance_open2,
                'neutral_resistance_open3': self.neutral_resistance_open3,
                'kv': self.kv,
                'bil': self.bil,
                'open': self.open,
                }


class AirCircuitBreaker(db.Model):
    __tablename__ = u'air_breaker'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    current_rating = db.Column(db.Numeric(6))

    # phase_number = db.Column(sqla.Enum('1', '3', '6', name="Phase number"))  # PhaseNum. 1=single phase, 3=triphase, 6=hexaphase
    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    # welded_cover = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'current_rating': self.current_rating,
                }


class Capacitor(db.Model):
    __tablename__ = u'capacitor'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    kv = db.Column(db.Float)  # voltage
    kvar = db.Column(db.Float)  # voltage
    bil = db.Column(db.Numeric(8))
    # #
    # # manufacturer_id = db.Column(
    # #     'manufacturer_id',
    # #     db.ForeignKey("manufacturer.id"),
    # #     nullable=False
    # # )
    # # manufacturer = relationship('Manufacturer', foreign_keys='Capacitor.manufacturer_id')
    #
    # # PhaseNum. 1=single phase, 3=triphase, 6=hexaphase
    # phase_number = db.Column(sqla.Enum('1', '3', '6', name="Phase number"))
    #
    # # frequency. Operating frequency
    # # frequency = db.Column(sqla.Enum('25', '50', '60', 'DC', name="Frequency"), default=db.text('25'))
    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    # # manufactured = db.Column(db.Integer)  # ManuYear. Year manufactured
    # # description = db.Column(db.UnicodeText())  # description. Describe the equipment function
    #
    # # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    # welded_cover = db.Column(db.Boolean)

    def __repr__(self):
        return self.__tablename__

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'kv': self.kv,
                'kvar': self.kvar,
                'bil': self.bil,
                }


class PowerSource(db.Model):
    __tablename__ = u'powersource'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    kv = db.Column(db.Float)  # voltage
    threephase = db.Column(db.Boolean)
    #
    # manufacturer_id = db.Column(
    #     'manufacturer_id',
    #     db.ForeignKey("manufacturer.id"),
    #     nullable=False
    # )
    #
    # manufacturer = relationship('Manufacturer', foreign_keys='PowerSource.manufacturer_id')
    # phase_number = db.Column(sqla.Enum('1', '3', '6', name="Phase number"))  # PhaseNum. 1=single phase, 3=triphase, 6=hexaphase
    # frequency = db.Column(sqla.Enum('25', '50', '60', 'DC', name="Frequency"), default=db.text('25'))  # frequency. Operating frequency
    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    # manufactured = db.Column(db.Integer)  # ManuYear. Year manufactured
    # description = db.Column(db.UnicodeText())  # description. Describe the equipment function

    # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    # welded_cover = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'kv': self.kv,
                'threephase': self.threephase,
                }


class SwitchGear(db.Model):
    __tablename__ = u'switchgear'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    current_rating = db.Column(db.Numeric(6))
    insulation_id = db.Column(db.Integer, db.ForeignKey("insulation.id"))
    insulation = db.relationship('Insulation', foreign_keys='SwitchGear.insulation_id')
    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    #
    # # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    # welded_cover = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'current_rating': self.current_rating,
                'insulation_id': self.insulation_id,
                'insulation': self.insulation,
                }


class InductionMachine(db.Model):
    __tablename__ = u'induction_machine'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    current_rating = db.Column(db.Numeric(6))
    hp = db.Column(db.String(50))
    kva = db.Column(db.String(50))
    pf = db.Column(db.String(50))

    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    #
    # # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    # welded_cover = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'current_rating': self.current_rating,
                'hp': self.hp,
                'kva': self.kva,
                'pf': self.pf,
                }


class SynchronousMachine(db.Model):
    __tablename__ = u'synchronous_machine'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    current_rating = db.Column(db.Numeric(6))
    hp = db.Column(db.String(50))
    kw = db.Column(db.String(50))

    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    # # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    # welded_cover = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'current_rating': self.current_rating,
                'hp': self.hp,
                'kw': self.kw,
                }


class Rectifier(db.Model):
    __tablename__ = u'rectifier'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    fluid_volume = db.Column(db.Float)
    sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    windings = db.Column(db.Integer)  # Windings. Number of windings in transformer

    # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    welded_cover = db.Column(db.Boolean)
    cooling_rating = db.Column(db.Integer)

    fluid_type_id = db.Column('fluid_type_id', db.ForeignKey("fluid_type.id"), nullable=True)
    fluid_type = db.relationship('FluidType', foreign_keys='Rectifier.fluid_type_id')

    fluid_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))
    fluid_level = db.relationship('FluidLevel', foreign_keys='Rectifier.fluid_level_id')

    gas_sensor_id = db.Column('gas_sensor_id', db.ForeignKey("gas_sensor.id"), nullable=False)
    gas_sensor = relationship('GasSensor', foreign_keys='Rectifier.gas_sensor_id')

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'fluid_volume': self.fluid_volume,
                'sealed': self.sealed,
                'windings': self.windings,
                'welded_cover': self.welded_cover,
                'cooling_rating': self.cooling_rating,
                'fluid_type_id': self.fluid_type_id,
                'fluid_type': self.fluid_type and self.fluid_type.serialize(),
                'fluid_level_id': self.fluid_level_id,
                'fluid_level': self.fluid_level and self.fluid_level.serialize(),
                'gas_sensor_id': self.gas_sensor_id,
                'gas_sensor': self.gas_sensor and self.gas_sensor.serialize(),
                }


class Inductance(db.Model):
    __tablename__ = u'inductance'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50))
    fluid_volume = db.Column(db.Float)
    sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.

    # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    welded_cover = db.Column(db.Boolean)
    cooling_rating = db.Column(db.Integer)

    fluid_type_id = db.Column('fluid_type_id', db.ForeignKey("fluid_type.id"), nullable=True)
    fluid_type = db.relationship('FluidType', foreign_keys='Inductance.fluid_type_id')

    fluid_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))
    fluid_level = db.relationship('FluidLevel', foreign_keys='Inductance.fluid_level_id')

    gas_sensor_id = db.Column('gas_sensor_id', db.ForeignKey("gas_sensor.id"), nullable=False)
    gas_sensor = relationship('GasSensor', foreign_keys='Inductance.gas_sensor_id')

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'fluid_volume': self.fluid_volume,
                'sealed': self.sealed,
                'welded_cover': self.welded_cover,
                'cooling_rating': self.cooling_rating,
                'fluid_type_id': self.fluid_type_id,
                'fluid_type': self.fluid_type and self.fluid_type.serialize(),
                'fluid_level_id': self.fluid_level_id,
                'fluid_level': self.fluid_level and self.fluid_level.serialize(),
                'gas_sensor_id': self.gas_sensor_id,
                'gas_sensor': self.gas_sensor and self.gas_sensor.serialize(),
                }


class Tank(db.Model):
    __tablename__ = u'tank'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)

    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    # manufactured = db.Column(db.Integer)  # ManuYear. Year manufactured
    # description = db.Column(db.UnicodeText())  # description. Describe the equipment function

    # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    welded_cover = db.Column(db.Boolean)
    fluid_type_id = db.Column('fluid_type_id', db.ForeignKey("fluid_type.id"), nullable=True)
    fluid_type = db.relationship('FluidType', foreign_keys='Tank.fluid_type_id')

    fluid_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))
    fluid_level = db.relationship('FluidLevel', foreign_keys='Tank.fluid_level_id')

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'welded_cover': self.welded_cover,
                'fluid_type_id': self.fluid_type_id,
                'fluid_type': self.fluid_type and self.fluid_type.serialize(),
                'fluid_level_id': self.fluid_level_id,
                'fluid_level': self.fluid_level and self.fluid_level.serialize(),
                }


class Switch(db.Model):
    __tablename__ = u'switch'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    current_rating = db.Column(db.Numeric(6))
    threephase = db.Column(db.Boolean)

    interrupting_medium_id = db.Column(db.Integer, db.ForeignKey("interrupting_medium.id"))
    interrupting_medium = db.relationship('InterruptingMedium', foreign_keys='Switch.interrupting_medium_id')

    # sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    #
    #
    # # welded_cover. Is cover welded. Important to planned work as it is much longer to remove cover
    # welded_cover = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'current_rating': self.current_rating,
                'threephase': self.threephase,
                'interrupting_medium_id': self.interrupting_medium_id,
                'interrupting_medium': self.interrupting_medium and self.interrupting_medium.serialize(),
                }


class Cable(db.Model):
    __tablename__ = u'cable'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    model = db.Column(db.String(50))
    sealed = db.Column(db.Boolean)  # sealed. Is equipment sealed.
    threephase = db.Column(db.Boolean)

    insulation_id = db.Column(db.Integer, db.ForeignKey("insulation.id"))
    insulation = db.relationship('Insulation', foreign_keys='Cable.insulation_id')
    # # Year manufactured
    # # manufactured = db.Column(db.Enum(",".join(map(str, range(1970, datetime.now().year))), name="years"))
    # manufactured = db.Column(db.Integer())
    # description = db.Column(db.UnicodeText())  # description. Describe the equipment function

    def __repr__(self):
        return "{} {} {}".format(self.__tablename__, self.name, self.serial)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'model': self.model,
                'sealed': self.sealed,
                'threephase': self.threephase,
                'insulation_id': self.insulation_id,
                'insulation': self.insulation and self.insulation.serialize(),
                }


class Equipment(db.Model):
    """
    Equipment.  records all information about the equipment.
    """
    __tablename__ = u'equipment'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))
    # EquipmentNumber: Equipment ID given by equipment owner.
    # Equipment number to uniquely identify equipment
    equipment_number = db.Column(db.String(50), nullable=False, index=True)
    # EquipmentSerialNum: Equipment ID given by manufacturer.
    # Index key, along with Equipment number to uniquely identify equipment
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    # EquipmentType. Define equipment by a single letter code. T:transformer, D; breaker etc...
    equipment_type_id = db.Column('equipment_type_id', db.ForeignKey("equipment_type.id"), nullable=False)
    equipment_type = relation('EquipmentType', backref='equipment')

    manufacturer_id = db.Column('manufacturer_id', db.ForeignKey("manufacturer.id"), nullable=False)
    manufacturer = relationship('Manufacturer', foreign_keys='Equipment.manufacturer_id')
    manufactured = db.Column(db.Integer)  # ManuYear. Year manufactured
    frequency = db.Column(sqla.Enum('25', '50', '60', 'DC', name="Frequency"), default=db.text('25'))
    description = db.Column(db.UnicodeText)
    # Location. Indicate the named placed where the equipement is.
    # Example, a main transformer is at site Budapest, and at localisation Church street.
    # Its the equivalent of the substation name.
    location_id = db.Column(
        'location_id',
        db.ForeignKey("location.id"),
        nullable=False
    )

    location = relationship('Location', backref='equipment')

    # EditedInfo. False no changes.  True Indicates the equipment info have changed and should update information
    # while importing data from Lab.
    modifier = db.Column(db.Boolean, nullable=True)

    comments = db.Column(db.Text)  # Comments relation

    # these fields should be related to every components test , it's not a preperty of the device its a test
    visual_date = db.Column(db.DateTime)  # VisualDate.  Date where was done the last visual inspection.
    # VisualInspectionBy. Who made the visual inspection. user relation
    visual_inspection_by_id = db.Column(
        'visual_inspection_by_id',
        sqla.ForeignKey("users_user.id"),
        nullable=False
    )
    visual_inspection_by = relationship('User', foreign_keys="Equipment.visual_inspection_by_id")

    assigned_to_id = db.Column(
        'assigned_to_id',
        db.ForeignKey("users_user.id"),
        nullable=False
    )
    assigned_to = relationship('User', foreign_keys="Equipment.assigned_to_id")

    visual_inspection_comments = db.Column(db.Text)  # VisualInspectionComments. Visual inspection comments,

    # test inspection of tap changer or characteristic ?
    nbr_of_tap_change_ltc = db.Column(db.Integer)  # NbrTapChange.  Number of tap change on LTC

    # its a separate norms table for all devices
    norm_id = db.Column(
        'norm_id',
        db.ForeignKey("norm.id"),
        nullable=False
    )

    norm = relationship('Norm', foreign_keys='Equipment.norm_id')

    # # its a state of a transformer / breaker /switch /motor / cable  not
    # upstream1 = db.Column(db.String(100))  # Upstream1. Upstream device name
    # upstream2 = db.Column(db.String(100))  # Upstream2. Upstream device name
    # upstream3 = db.Column(db.String(100))  # Upstream3. Upstream device name
    # upstream4 = db.Column(db.String(100))  # Upstream4. Upstream device name
    # upstream5 = db.Column(db.String(100))  # Upstream5. Upstream device name
    #
    # downstream1 = db.Column(db.String(100))  # Downstream1. Downstream device name
    # downstream2 = db.Column(db.String(100))  # Downstream2. Downstream device name
    # downstream3 = db.Column(db.String(100))  # Downstream3. Downstream device name
    # downstream4 = db.Column(db.String(100))  # Downstream4. Downstream device name
    # downstream5 = db.Column(db.String(100))  # Downstream5. Downstream device name

    tie_location = db.Column(db.Boolean)  # TieLocation. Tie device location
    tie_maintenance_state = db.Column(db.Integer)  # TieMaintenanceState. Tie is open or closed during maintenance
    tie_status = db.Column(db.Integer)  # TieAnalysisState.

    phys_position = db.Column(db.Integer)

    # device property for all equipment
    tension4 = db.Column(db.Float(53))  # Voltage4

    # Validated. Indicate equipment info has been validated and can be imported.
    validated = db.Column(db.Boolean)

    # InValidation. If true, equipment information from lab must be updated before get imported into the main DB
    invalidation = db.Column(db.Boolean)

    # PrevSerielNum. If InValidation is true, indicate what was the previous value to retreive the correct equipment
    # information from Lab
    prev_serial_number = db.Column(db.String(50))

    # PrevEquipmentNum.
    # If InValidation is true,
    # indicate what was the previous value to retreive the correct equipment information from Lab
    prev_equipment_number = db.Column(db.String(50))

    # Sibling. Unique Common Index with the other siblings.  If 0 then no sibling
    # id of a similar equipment
    sibling = db.Column(db.Integer)

    def __repr__(self):
        return "{} {} {}".format(self.name, self.serial, self.equipment_number)

    # def __init__(self, **kwargs):
    #     self.visual_inspection_by_id = int(kwargs.get('visual_inspection_by_id'))
    #     self.norm_id = int(kwargs.get('norm_id'))
    #     self.equipment_type_id = int(kwargs.get('equipment_type_id'))
    #     self.equipment_number = int(kwargs.get('equipment_number'))
    #     self.location_id = int(kwargs.get('location_id'))
    #     self.manufacturer_id = int(kwargs.get('manufacturer_id'))
    #     self.assigned_to_id = int(kwargs.get('assigned_to_id'))
    #     self.serial = int(kwargs.get('serial'))
    #     self.frequency = cast(kwargs.get('frequency'), Enum(name='Frequency'))
    #     # db.Enum('25', '50', '60', 'DC', name="Frequency")


    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'serial': self.serial,
                'equipment_number': self.equipment_number,
                'equipment_type_id': self.equipment_type_id,
                'equipment_type': self.equipment_type and self.equipment_type.serialize(),
                'manufacturer_id': self.manufacturer_id,
                'manufacturer': self.manufacturer and self.manufacturer.serialize(),
                'manufactured': self.manufactured,
                'frequency': self.frequency,
                'description': self.description,
                'location_id': self.location_id,
                'location': self.location and self.location.serialize(),
                'modifier': self.modifier,
                'comments': self.comments,
                'visual_date': dump_datetime(self.visual_date),
                'visual_inspection_by_id': self.visual_inspection_by_id,
                'visual_inspection_by': self.visual_inspection_by and self.visual_inspection_by.serialize(),
                'assigned_to_id': self.assigned_to_id,
                'assigned_to': self.assigned_to and self.assigned_to.serialize(),
                'visual_inspection_comments': self.visual_inspection_comments,
                'nbr_of_tap_change_ltc': self.nbr_of_tap_change_ltc,
                'norm_id': self.norm_id,
                'norm': self.norm and self.norm.serialize(),
                # 'upstream1': self.upstream1,
                # 'upstream2': self.upstream2,
                # 'upstream3': self.upstream3,
                # 'upstream4': self.upstream4,
                # 'upstream5': self.upstream5,
                # 'downstream1': self.downstream1,
                # 'downstream2': self.downstream2,
                # 'downstream3': self.downstream3,
                # 'downstream4': self.downstream4,
                # 'downstream5': self.downstream5,
                'tie_location': self.tie_location,
                'tie_maintenance_state': self.tie_maintenance_state,
                'tie_status': self.tie_status,
                'phys_position': self.phys_position,
                'tension4': self.tension4,
                'validated': self.validated,
                'invalidation': self.invalidation,
                'prev_serial_number': self.prev_serial_number,
                'prev_equipment_number': self.prev_equipment_number,
                'sibling': self.sibling,
                }


class Norm(db.Model):
    __tablename__ = u'norm'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), index=True)
    table_name = db.Column(db.String(50), index=True)
    # type = db.relationship('NormType', backref='norm')

    # NormPHY.  Fluid physical properties norms
    # NormDissolvedGas. Fluid dissolved gas norms
    # NormFluid# NormFur. Fluid furan norms
    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'table_name': self.table_name,
                }


class Recommendation(db.Model):
    __tablename__ = u'recommendation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), index=True)
    code = db.Column(db.String(50), index=True)
    description = db.Column(db.UnicodeText())
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_type.id'))
    test_type = relationship('TestType', foreign_keys='Recommendation.test_type_id')

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'code': self.code,
                'description': self.description,
                'test_type_id': self.test_type_id,
                'test_type': self.test_type and self.test_type.serialize(),
                }


class TestRecommendation(db.Model):
    __tablename__ = u'test_recommendation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    recommendation_id = db.Column(db.ForeignKey("recommendation.id"))
    recommendation = db.relationship('Recommendation', backref='test_recommendation')
    recommendation_notes = db.Column(db.Text)
    user_id = db.Column(db.ForeignKey("users_user.id"))
    user = db.relationship('User', foreign_keys='TestRecommendation.user_id')
    date_created = db.Column(db.DateTime)
    date_updated = db.Column(db.DateTime)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='test_recommendation')

    def __repr__(self):
        return "{} {} by {}".format(self.id, self.recommendation, self.user)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'recommendation_id': self.recommendation_id,
                'recommendation': self.recommendation and self.recommendation.serialize(),
                'recommendation_notes': self.recommendation_notes,
                'user_id': self.user_id,
                'user': self.user and self.user.serialize(),
                'date_created': self.date_created,
                'date_updated': self.date_updated,
                }


class GasLevel(db.Model):
    # 0-normal, 1-caution, 2- danger and 3-extreme
    __tablename__ = u'gas_level'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, index=True, unique=True)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class InterruptingMedium(db.Model):
    __tablename__ = u'interrupting_medium'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class BreakerMechanism(db.Model):
    __tablename__ = u'breaker_mechanism'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class Insulation(db.Model):
    __tablename__ = u'insulation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class Syringe(db.Model):
    __tablename__ = u'syringe'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    serial = db.Column(db.String(50), nullable=False, index=True, unique=True)
    lab_id = db.Column('lab_id', db.ForeignKey('lab.id'), nullable=True)
    lab = db.relationship('Lab', backref='syringe')

    def __repr__(self):
        return self.serial

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'serial': self.serial,
                'lab_id': self.lab_id,
                'lab': self.lab and self.lab.serialize(),
                }


class TestReason(db.Model):
    __tablename__ = 'test_reason'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), index=True)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class TestStatus(db.Model):
    __tablename__ = 'test_status'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    code = db.Column(db.String(50), index=True)
    name = db.Column(db.String(50), index=True)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'code': self.code
                }


class CampaignStatus(db.Model):
    __tablename__ = 'campaign_status'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    code = db.Column(db.String(50))
    name = db.Column(db.String(50))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'code': self.code
                }


class TestSchedule(db.Model):
    """
    Schedule. List work, periodic or not, to be done on individual equipment.
    Tests profile are used to define the work to be done.
    If work are very specific, then use description to detail the work required.
    """

    __tablename__ = u'schedule'

    # EquipmentSerialNum: Equipment ID given by manufacturer.
    # Index key, along with Equipment number to uniquely identify equipment
    # NoSerieEquipe = Column(db.String(50), primary_key=True,
    #                        nullable=False)
    # EquipmentNumber: Equipment ID given by equipment owner.
    # Index key, along with Equipment number to uniquely identify equipment
    # NoEquipement = Column(db.String(50), primary_key=True,
    #                       nullable=False)

    equipment_id = db.Column('equipment_id', sqla.ForeignKey("equipment.id"), nullable=False)
    equipment = db.relationship('Equipment', foreign_keys='TestSchedule.equipment_id')

    start_date = db.Column(db.DateTime, primary_key=True, nullable=False)  # StartDate. Starting date of periodic task
    period_years = db.Column(db.Integer, server_default=db.text("0"))  # AnnualPeriod. Number of year between tasks
    period_months = db.Column(db.Integer, server_default=db.text("0"))  # AnnualPeriod. Number of month between tasks
    period_days = db.Column(db.Integer, server_default=db.text("0"))  # AnnualPeriod. Number of days between tasks

    # Worker. Who did the work or was responsible for
    assigned_to_id = db.Column(
        'assigned_to_id',
        db.ForeignKey("users_user.id"),
        nullable=False
    )
    assigned_to = db.relationship('User', backref='schedule')
    recurring = db.Column(db.Boolean)  # RecurrentTask. Indicate if task takes place periodically

    # RecallDays. How many days ahead message before work takes place
    notify_before_in_days = db.Column(db.Integer, server_default=db.text("0"))

    description = db.Column(db.UnicodeText())

    # prof_fluid = Column(db.String(25))  # Prof_Fluid. Which fluid tests profile should be used
    # prof_elec = Column(db.String(25))  # Prof_Elec.  Which electrical tests profile should be used
    # prof_mec = Column(db.String(25))  # Prof_Mec.  Which mechanical tests profile should be used

    tests_to_perform = db.Column(db.Integer, db.ForeignKey('test_type.id'))
    tests = relationship("TestType")

    order = db.Column(db.Integer, primary_key=True, nullable=False)  # WorkOrderNum

    def __repr__(self):
        return "{} {}".format(self.equipment, self.start_date)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'equipment_id': self.equipment_id,
                'equipment': self.equipment and self.equipment.serialize(),
                'start_date': dump_datetime(self.start_date),
                'period_years': self.period_years,
                'period_months': self.period_months,
                'period_days': self.period_days,
                'assigned_to_id': self.assigned_to_id,
                'assigned_to': self.assigned_to and self.assigned_to.serialize(),
                'recurring': self.recurring,
                'notify_before_in_days': self.notify_before_in_days,
                'description': self.description,
                'tests_to_perform': self.tests_to_perform,
                'tests': self.tests and self.tests.serialize(),
                'order': self.order,
                }


class TestType(db.Model):
    __tablename__ = u'test_type'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, index=True)
    group_id = db.Column(db.Integer)
    # group_id = db.Column(db.Integer, db.ForeignKey('test_type.id'), nullable=True)
    # group = relationship('TestType', backref="test_type")
    is_group = db.Column(db.Boolean, nullable=False, default=False)
    # test_type_result_table = db.relationship("TestTypeResultTable", back_populates="test_type")

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'group_id': self.group_id,
                'is_group': self.is_group,
                }


class TestTypeResultTable(db.Model):
    __tablename__ = u'test_type_result_table'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_type.id'))
    test_type = relationship('TestType', backref="test_type_result_table")
    # test_type = db.relationship('TestType', back_populates="test_type_result_table")
    test_result_table_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "{} - {}".format(self.test_type, self.test_result_table_name)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_type_id': self.test_type_id,
                'test_type': self.test_type and self.test_type.serialize(),
                'test_result_table_name': self.test_result_table_name,
                }


class TestResult(db.Model):
    """
    TestResults. Contains test results. It is a "tablepart" of campaign
    """
    __tablename__ = 'test_result'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"))
    campaign = db.relationship('Campaign', backref='test_result')

    # Reason: Code indicating why the analysis was performed.
    # Mainly use for oil sampling.
    reason_id = db.Column('test_reason_id', db.ForeignKey("test_reason.id"), nullable=True)
    test_reason = db.relationship('TestReason', backref='test_result')

    # Date filled by labratory when analysis was done
    # AnalysisDate: Date the analysis was performed
    date_analyse = db.Column(db.DateTime, index=True)

    # AnalysisType: Analysis type performed on equipment:
    # (insulating fluid  material from equipment , it should be a relation )
    test_type_id = db.Column(db.Integer, db.ForeignKey("test_type.id"))
    test_type = db.relationship('TestType', backref='test_result')

    # PointCode: Code indicating where the oil sample was done
    sampling_point_id = db.Column('sampling_point_id', db.ForeignKey("sampling_point.id"), nullable=True)
    sampling_point = db.relationship('SamplingPoint', backref='test_result')

    # Status: Code indicating the Analysis status.
    # Analysis is a process with several steps and each one has a code.
    test_status_id = db.Column('status_id', sqla.ForeignKey("test_status.id"), nullable=True)
    test_status = db.relationship('TestStatus', backref='test_result')

    equipment_id = db.Column('equipment_id', db.ForeignKey("equipment.id"))
    equipment = db.relationship('Equipment', foreign_keys='TestResult.equipment_id')
    fluid_profile_id = db.Column('fluid_profile_id', db.ForeignKey("fluid_profile.id"))
    fluid_profile = db.relationship('FluidProfile', foreign_keys='TestResult.fluid_profile_id')
    electrical_profile_id = db.Column('electrical_profile_id', db.ForeignKey("electrical_profile.id"))
    electrical_profile = db.relationship('ElectricalProfile', foreign_keys='TestResult.electrical_profile_id')

    # PercentRatio: Indicate if the TTR was done using Percent ratio or Ratio. Used with TTR table
    # Comes from equipment
    # specific electrical test on winding.  TTR - tranformer term ...
    # true when user decided to use percent ratio for ttr
    percent_ratio = db.Column(db.Boolean)
    material_id = db.Column(db.ForeignKey("material.id"))
    material = db.relationship('Material', backref='test_result')
    fluid_type_id = db.Column(db.ForeignKey("fluid_type.id"))
    fluid_type = db.relationship('FluidType', foreign_keys='TestResult.fluid_type_id')
    performed_by_id = db.Column(db.ForeignKey("users_user.id"))
    performed_by = db.relationship('User', foreign_keys='TestResult.performed_by_id')
    lab_id = db.Column(db.ForeignKey("lab.id"), nullable=False)
    lab = db.relationship('Lab', backref='test_result')
    lab_contract_id = db.Column(db.ForeignKey("contract.id"))
    lab_contract = db.relationship('Contract', foreign_keys='TestResult.lab_contract_id')
    seringe_num = db.Column(db.String(50))
    mws = db.Column(db.Float(53))
    temperature = db.Column(db.Float(53))
    containers = db.Column(db.Float(53))
    transmission = db.Column(db.Boolean)
    charge = db.Column(db.Float(53))

    remark = db.Column(db.Text)
    modifier = db.Column(db.Boolean)
    repair_date = db.Column(db.DateTime)
    repair_description = db.Column(db.Text)
    ambient_air_temperature = db.Column(db.Float(53))

    # electriacal profile fields
    bushing = db.Column(db.Boolean(False))
    winding = db.Column(db.Boolean(False))
    insulation_pf = db.Column(db.Boolean(False))
    insulation = db.Column(db.Boolean(False))
    visual_inspection = db.Column(db.Boolean(False))
    resistance = db.Column(db.Boolean(False))
    degree = db.Column(db.Boolean(False))
    turns = db.Column(db.Boolean(False))

    # fluid profile field
    # syringe
    gas = db.Column(db.Boolean(False))
    water = db.Column(db.Boolean(False))
    furans = db.Column(db.Boolean(False))
    inhibitor = db.Column(db.Boolean(False))
    pcb = db.Column(db.Boolean(False))
    qty = db.Column(db.Integer)  # qty Syringe
    sampling = db.Column(db.Integer)
    # jar
    dielec = db.Column(db.Boolean(False))
    acidity = db.Column(db.Boolean(False))
    density = db.Column(db.Boolean(False))
    pcb_jar = db.Column(db.Boolean(False))
    inhibitor_jar = db.Column(db.Boolean(False))
    point = db.Column(db.Boolean(False))
    dielec_2 = db.Column(db.Boolean(False))
    color = db.Column(db.Boolean(False))
    pf = db.Column(db.Boolean(False))
    particles = db.Column(db.Boolean(False))
    metals = db.Column(db.Boolean(False))
    viscosity = db.Column(db.Boolean(False))
    dielec_d = db.Column(db.Boolean(False))
    ift = db.Column(db.Boolean(False))
    pf_100 = db.Column(db.Boolean(False))
    furans_f = db.Column(db.Boolean(False))
    water_w = db.Column(db.Boolean(False))
    corr = db.Column(db.Boolean(False))
    dielec_i = db.Column(db.Boolean(False))
    visual = db.Column(db.Boolean(False))
    qty_jar = db.Column(db.Integer)
    sampling_jar = db.Column(db.Integer)
    # vial
    pcb_vial = db.Column(db.Boolean(False))
    antioxidant = db.Column(db.Boolean(False))
    qty_vial = db.Column(db.Integer)
    sampling_vial = db.Column(db.Integer)


    def __repr__(self):
        return "{} - {}".format(self.campaign, self.test_type)

    @property
    def test_model(self):
        result_table = db.session.query(TestTypeResultTable).filter_by(test_type_id=self.test_type_id).first()
        if result_table:
            return get_class_by_tablename(result_table.test_result_table_name)

    @property
    def analysis_number(self):
        if self.campaign:
            return "{}{}".format(self.id, self.campaign.created_by.initials)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'reason_id': self.reason_id,
            'test_reason': self.test_reason and self.test_reason.serialize(),
            'date_analyse': dump_datetime(self.date_analyse),
            'test_type_id': self.test_type_id,
            'test_type': self.test_type and self.test_type.serialize(),
            'sampling_point_id': self.sampling_point_id,
            'sampling_point': self.sampling_point and self.sampling_point.serialize(),
            'test_status_id': self.test_status_id,
            'test_status': self.test_status and self.test_status.serialize(),
            'equipment_id': self.equipment_id,
            'equipment': self.equipment and self.equipment.serialize(),
            'fluid_profile_id': self.fluid_profile_id,
            'fluid_profile': self.fluid_profile and self.fluid_profile.serialize(),
            'electrical_profile_id': self.electrical_profile_id,
            'electrical_profile': self.electrical_profile and self.electrical_profile.serialize(),
            'percent_ratio': self.percent_ratio,
            'analysis_number': self.analysis_number,
            'material_id': self.material_id,
            'material': self.material and self.material.serialize(),
            'fluid_type_id': self.fluid_type_id,
            'fluid_type': self.fluid_type and self.fluid_type.serialize(),
            'charge': self.charge,
            'performed_by_id': self.performed_by_id,
            'performed_by': self.performed_by and self.performed_by.serialize(),
            'transmission': self.transmission,
            'lab_id': self.lab_id,
            'lab': self.lab and self.lab.serialize(),
            'mws': self.mws,
            'temperature': self.temperature,
            'containers': self.containers,
            'lab_contract_id': self.lab_contract_id,
            'lab_contract': self.lab_contract and self.lab_contract.serialize(),
            'seringe_num': self.seringe_num,
            'remark': self.remark,
            'modifier': self.modifier,
            'repair_date': dump_datetime(self.repair_date),
            'repair_description': self.repair_description,
            'ambient_air_temperature': self.ambient_air_temperature,
            'bushing': self.bushing,
            'winding': self.winding,
            'insulation_pf': self.insulation_pf,
            'insulation': self.insulation,
            'visual_inspection': self.visual_inspection,
            'resistance': self.resistance,
            'degree': self.degree,
            'turns': self.turns,
            'gas': self.gas,
            'water': self.water,
            'furans': self.furans,
            'inhibitor': self.inhibitor,
            'pcb': self.pcb,
            'qty': self.qty,
            'sampling': self.sampling,
            'dielec': self.dielec,
            'acidity': self.acidity,
            'density': self.density,
            'pcb_jar': self.pcb_jar,
            'inhibitor_jar': self.inhibitor_jar,
            'point': self.point,
            'dielec_2': self.dielec_2,
            'color': self.color,
            'pf': self.pf,
            'particles': self.particles,
            'metals': self.metals,
            'viscosity': self.viscosity,
            'dielec_d': self.dielec_d,
            'ift': self.ift,
            'pf_100': self.pf_100,
            'furans_f': self.furans_f,
            'water_w': self.water_w,
            'corr': self.corr,
            'dielec_i': self.dielec_i,
            'visual': self.visual,
            'qty_jar': self.qty_jar,
            'sampling_jar': self.sampling_jar,
            'pcb_vial': self.pcb_vial,
            'antioxidant': self.antioxidant,
            'qty_vial': self.qty_vial,
            'sampling_vial': self.sampling_vial,
            'tests': self.test_model and [
                test.serialize() for test in db.session.query(self.test_model)
                    .filter_by(test_result_id=self.id)
            ],
            'test_sampling_cards': [
                card.serialize() for card in db.session.query(TestSamplingCard)
                    .filter_by(test_result_id=self.id)
            ],
            'test_recommendations': [
                item.serialize() for item in db.session.query(TestRecommendation)
                    .filter_by(test_result_id=self.id)
            ]
        }


class GasketCondition(db.Model):
    """Predefined: (Good, Leak-wet, Leak-flowing, Not-visible, Not appl, See notes)"""
    __tablename__ = 'gasket_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class GasRelay(db.Model):
    """Predefined: (Good, 100cc -1/2 full, 200cc - full, Not appl, See notes)"""
    __tablename__ = 'gas_relay'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class FluidLevel(db.Model):
    """Predefined: (Good, Very Low, Low, High, Unavailable, Not readable, Not-visible, Not appl, See notes)"""
    __tablename__ = 'fluid_level'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class PressureUnit(db.Model):
    """(kPa, psi)"""
    __tablename__ = 'pressure_unit'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class ValveCondition(db.Model):
    """Predefined: (Good, Leak-wet, Leak-flowing, Unavalable, Not-visible, Not appl, See notes)"""
    __tablename__ = 'valve_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class PumpCondition(db.Model):
    """Predefined: (Working, Inoperable, Vibrating, Noisy, Leak-wet, Leak-flowing, Not appl, See notes)"""
    __tablename__ = 'pump_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class OverallCondition(db.Model):
    """Predefined: (Good, Dirty, Leak-wet, Rusted, Not appl. See notes)"""
    __tablename__ = 'overall_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class PaintTypes(db.Model):
    """Predefined: (Good, White, Blue, Brown, Pink, Defective, Unavailable, Not appl., See notes)"""
    __tablename__ = 'paint_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class TapCounterStatus(db.Model):
    """Predefined: (Good, Defective, Not readable, Not appl., See notes)"""
    __tablename__ = 'tap_counter_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class TapFilterCondition(db.Model):
    """Predefined: (Good, Clogged, Defective, Leak-wet, Leak-flowing, Not appl, See notes)"""
    __tablename__ = 'tap_filter_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class FanCondition(db.Model):
    """Predefined: (Working, Inoperable, Vibrating, Noisy, Not appl, See notes)"""
    __tablename__ = 'fan_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class ConnectionCondition(db.Model):
    """Predefined: (Good, Sealed, Not appl., See notes)"""
    __tablename__ = 'connection_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class FoundationCondition(db.Model):
    """Predefined: (Good, Not to level, Dirty, Damaged, Not appl, See notes)"""
    __tablename__ = 'foundation_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class HeatingCondition(db.Model):
    """Predefined: (Good, Defective Res, Thermal_fault, Not appl., See notes)"""
    __tablename__ = 'heating_condition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class BushingTest(db.Model):
    """Bushing. Bushing test result"""

    __tablename__ = u'bushing_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='bushing_test')
    h1 = db.Column(db.Float(53))  # Remaining are as is
    h2 = db.Column(db.Float(53))
    h3 = db.Column(db.Float(53))
    hn = db.Column(db.Float(53))
    h1c1 = db.Column(db.Float(53))
    h2c1 = db.Column(db.Float(53))
    h3c1 = db.Column(db.Float(53))
    hnc1 = db.Column(db.Float(53))
    h1c2 = db.Column(db.Float(53))
    h2c2 = db.Column(db.Float(53))
    h3c2 = db.Column(db.Float(53))
    hnc2 = db.Column(db.Float(53))
    x1 = db.Column(db.Float(53))
    x2 = db.Column(db.Float(53))
    x3 = db.Column(db.Float(53))
    xn = db.Column(db.Float(53))
    x1c1 = db.Column(db.Float(53))
    x2c1 = db.Column(db.Float(53))
    x3c1 = db.Column(db.Float(53))
    xnc1 = db.Column(db.Float(53))
    x1c2 = db.Column(db.Float(53))
    x2c2 = db.Column(db.Float(53))
    x3c2 = db.Column(db.Float(53))
    xnc2 = db.Column(db.Float(53))
    t1 = db.Column(db.Float(53))
    t2 = db.Column(db.Float(53))
    t3 = db.Column(db.Float(53))
    tn = db.Column(db.Float(53))
    t1c1 = db.Column(db.Float(53))
    t2c1 = db.Column(db.Float(53))
    t3c1 = db.Column(db.Float(53))
    tnc1 = db.Column(db.Float(53))
    t1c2 = db.Column(db.Float(53))
    t2c2 = db.Column(db.Float(53))
    t3c2 = db.Column(db.Float(53))
    tnc2 = db.Column(db.Float(53))
    temperature = db.Column(db.Float(53))
    facteur = db.Column(db.Float(53))
    facteur1 = db.Column(db.Float(53))
    facteur2 = db.Column(db.Float(53))
    q1 = db.Column(db.Float(53))
    q2 = db.Column(db.Float(53))
    q3 = db.Column(db.Float(53))
    qn = db.Column(db.Float(53))
    q1c1 = db.Column(db.Float(53))
    q2c1 = db.Column(db.Float(53))
    q3c1 = db.Column(db.Float(53))
    qnc1 = db.Column(db.Float(53))
    q1c2 = db.Column(db.Float(53))
    q2c2 = db.Column(db.Float(53))
    q3c2 = db.Column(db.Float(53))
    qnc2 = db.Column(db.Float(53))
    facteur3 = db.Column(db.Float(53))
    humidity = db.Column(db.Float(53))

    test_kv_h1 = db.Column(db.Float(53))
    test_kv_h2 = db.Column(db.Float(53))
    test_kv_h3 = db.Column(db.Float(53))
    test_kv_hn = db.Column(db.Float(53))
    test_kv_x1 = db.Column(db.Float(53))
    test_kv_x2 = db.Column(db.Float(53))
    test_kv_x3 = db.Column(db.Float(53))
    test_kv_xn = db.Column(db.Float(53))
    test_kv_t1 = db.Column(db.Float(53))
    test_kv_t2 = db.Column(db.Float(53))
    test_kv_t3 = db.Column(db.Float(53))
    test_kv_tn = db.Column(db.Float(53))
    test_kv_q1 = db.Column(db.Float(53))
    test_kv_q2 = db.Column(db.Float(53))
    test_kv_q3 = db.Column(db.Float(53))
    test_kv_qn = db.Column(db.Float(53))

    test_pfc2_h1 = db.Column(db.Float(53))
    test_pfc2_h2 = db.Column(db.Float(53))
    test_pfc2_h3 = db.Column(db.Float(53))
    test_pfc2_hn = db.Column(db.Float(53))
    test_pfc2_x1 = db.Column(db.Float(53))
    test_pfc2_x2 = db.Column(db.Float(53))
    test_pfc2_x3 = db.Column(db.Float(53))
    test_pfc2_xn = db.Column(db.Float(53))
    test_pfc2_t1 = db.Column(db.Float(53))
    test_pfc2_t2 = db.Column(db.Float(53))
    test_pfc2_t3 = db.Column(db.Float(53))
    test_pfc2_tn = db.Column(db.Float(53))
    test_pfc2_q1 = db.Column(db.Float(53))
    test_pfc2_q2 = db.Column(db.Float(53))
    test_pfc2_q3 = db.Column(db.Float(53))
    test_pfc2_qn = db.Column(db.Float(53))
    facteurn = db.Column(db.Float(53))
    facteurn1 = db.Column(db.Float(53))
    facteurn2 = db.Column(db.Float(53))
    facteurn3 = db.Column(db.Float(53))

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'h1': self.h1,
                'h2': self.h2,
                'h3': self.h3,
                'hn': self.hn,
                'h1c1': self.h1c1,
                'h2c1': self.h2c1,
                'h3c1': self.h3c1,
                'hnc1': self.hnc1,
                'h1c2': self.h1c2,
                'h2c2': self.h2c2,
                'h3c2': self.h3c2,
                'hnc2': self.hnc2,
                'x1': self.x1,
                'x2': self.x2,
                'x3': self.x3,
                'xn': self.xn,
                'x1c1': self.x1c1,
                'x2c1': self.x2c1,
                'x3c1': self.x3c1,
                'xnc1': self.xnc1,
                'x1c2': self.x1c2,
                'x2c2': self.x2c2,
                'x3c2': self.x3c2,
                'xnc2': self.xnc2,
                't1': self.t1,
                't2': self.t2,
                't3': self.t3,
                'tn': self.tn,
                't1c1': self.t1c1,
                't2c1': self.t2c1,
                't3c1': self.t3c1,
                'tnc1': self.tnc1,
                't1c2': self.t1c2,
                't2c2': self.t2c2,
                't3c2': self.t3c2,
                'tnc2': self.tnc2,
                'temperature': self.temperature,
                'facteur': self.facteur,
                'facteur1': self.facteur1,
                'facteur2': self.facteur2,
                'q1': self.q1,
                'q2': self.q2,
                'q3': self.q3,
                'qn': self.qn,
                'q1c1': self.q1c1,
                'q2c1': self.q2c1,
                'q3c1': self.q3c1,
                'qnc1': self.qnc1,
                'q1c2': self.q1c2,
                'q2c2': self.q2c2,
                'q3c2': self.q3c2,
                'qnc2': self.qnc2,
                'facteur3': self.facteur3,
                'humidity': self.humidity,
                'test_kv_h1': self.test_kv_h1,
                'test_kv_h2': self.test_kv_h2,
                'test_kv_h3': self.test_kv_h3,
                'test_kv_hn': self.test_kv_hn,
                'test_kv_x1': self.test_kv_x1,
                'test_kv_x2': self.test_kv_x2,
                'test_kv_x3': self.test_kv_x3,
                'test_kv_xn': self.test_kv_xn,
                'test_kv_t1': self.test_kv_t1,
                'test_kv_t2': self.test_kv_t2,
                'test_kv_t3': self.test_kv_t3,
                'test_kv_tn': self.test_kv_tn,
                'test_kv_q1': self.test_kv_q1,
                'test_kv_q2': self.test_kv_q2,
                'test_kv_q3': self.test_kv_q3,
                'test_kv_qn': self.test_kv_qn,
                'test_pfc2_h1': self.test_pfc2_h1,
                'test_pfc2_h2': self.test_pfc2_h2,
                'test_pfc2_h3': self.test_pfc2_h3,
                'test_pfc2_hn': self.test_pfc2_hn,
                'test_pfc2_x1': self.test_pfc2_x1,
                'test_pfc2_x2': self.test_pfc2_x2,
                'test_pfc2_x3': self.test_pfc2_x3,
                'test_pfc2_xn': self.test_pfc2_xn,
                'test_pfc2_t1': self.test_pfc2_t1,
                'test_pfc2_t2': self.test_pfc2_t2,
                'test_pfc2_t3': self.test_pfc2_t3,
                'test_pfc2_tn': self.test_pfc2_tn,
                'test_pfc2_q1': self.test_pfc2_q1,
                'test_pfc2_q2': self.test_pfc2_q2,
                'test_pfc2_q3': self.test_pfc2_q3,
                'test_pfc2_qn': self.test_pfc2_qn,
                'facteurn': self.facteurn,
                'facteurn1': self.facteurn1,
                'facteurn2': self.facteurn2,
                'facteurn3': self.facteurn3,
                }


class WindingTest(db.Model):
    """Bushing data and test results"""
    __tablename__ = u'winding_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='winding_test')
    test_kv1 = db.Column(db.Float(53))  # Remaining field names are equivalent
    test_kv2 = db.Column(db.Float(53))
    test_kv3 = db.Column(db.Float(53))
    test_kv4 = db.Column(db.Float(53))
    test_kv5 = db.Column(db.Float(53))
    test_kv6 = db.Column(db.Float(53))
    test_kv7 = db.Column(db.Float(53))
    test_kv8 = db.Column(db.Float(53))
    test_kv9 = db.Column(db.Float(53))
    test_kv10 = db.Column(db.Float(53))
    m_meter1 = db.Column(db.Float(53))
    m_meter2 = db.Column(db.Float(53))
    m_meter3 = db.Column(db.Float(53))
    m_meter4 = db.Column(db.Float(53))
    m_meter5 = db.Column(db.Float(53))
    m_meter6 = db.Column(db.Float(53))
    m_meter7 = db.Column(db.Float(53))
    m_meter8 = db.Column(db.Float(53))
    m_meter9 = db.Column(db.Float(53))
    m_meter10 = db.Column(db.Float(53))
    m_multiplier1 = db.Column(db.Float(53))
    m_multiplier2 = db.Column(db.Float(53))
    m_multiplier3 = db.Column(db.Float(53))
    m_multiplier4 = db.Column(db.Float(53))
    m_multiplier5 = db.Column(db.Float(53))
    m_multiplier6 = db.Column(db.Float(53))
    m_multiplier7 = db.Column(db.Float(53))
    m_multiplier8 = db.Column(db.Float(53))
    m_multiplier9 = db.Column(db.Float(53))
    m_multiplier10 = db.Column(db.Float(53))
    w_meter1 = db.Column(db.Float(53))
    w_meter2 = db.Column(db.Float(53))
    w_meter3 = db.Column(db.Float(53))
    w_meter4 = db.Column(db.Float(53))
    w_meter5 = db.Column(db.Float(53))
    w_meter6 = db.Column(db.Float(53))
    w_meter7 = db.Column(db.Float(53))
    w_meter8 = db.Column(db.Float(53))
    w_meter9 = db.Column(db.Float(53))
    w_meter10 = db.Column(db.Float(53))
    w_multiplier1 = db.Column(db.Float(53))
    w_multiplier2 = db.Column(db.Float(53))
    w_multiplier3 = db.Column(db.Float(53))
    w_multiplier4 = db.Column(db.Float(53))
    w_multiplier5 = db.Column(db.Float(53))
    w_multiplier6 = db.Column(db.Float(53))
    w_multiplier7 = db.Column(db.Float(53))
    w_multiplier8 = db.Column(db.Float(53))
    w_multiplier9 = db.Column(db.Float(53))
    w_multiplier10 = db.Column(db.Float(53))
    type_doble = db.Column(db.Boolean)
    humidity = db.Column(db.Float(53))  # Humidity

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'test_kv1': self.test_kv1,
                'test_kv2': self.test_kv2,
                'test_kv3': self.test_kv3,
                'test_kv4': self.test_kv4,
                'test_kv5': self.test_kv5,
                'test_kv6': self.test_kv6,
                'test_kv7': self.test_kv7,
                'test_kv8': self.test_kv8,
                'test_kv9': self.test_kv9,
                'test_kv10': self.test_kv10,
                'm_meter1': self.m_meter1,
                'm_meter2': self.m_meter2,
                'm_meter3': self.m_meter3,
                'm_meter4': self.m_meter4,
                'm_meter5': self.m_meter5,
                'm_meter6': self.m_meter6,
                'm_meter7': self.m_meter7,
                'm_meter8': self.m_meter8,
                'm_meter9': self.m_meter9,
                'm_meter10': self.m_meter10,
                'm_multiplier1': self.m_multiplier1,
                'm_multiplier2': self.m_multiplier2,
                'm_multiplier3': self.m_multiplier3,
                'm_multiplier4': self.m_multiplier4,
                'm_multiplier5': self.m_multiplier5,
                'm_multiplier6': self.m_multiplier6,
                'm_multiplier7': self.m_multiplier7,
                'm_multiplier8': self.m_multiplier8,
                'm_multiplier9': self.m_multiplier9,
                'm_multiplier10': self.m_multiplier10,
                'w_meter1': self.w_meter1,
                'w_meter2': self.w_meter2,
                'w_meter3': self.w_meter3,
                'w_meter4': self.w_meter4,
                'w_meter5': self.w_meter5,
                'w_meter6': self.w_meter6,
                'w_meter7': self.w_meter7,
                'w_meter8': self.w_meter8,
                'w_meter9': self.w_meter9,
                'w_meter10': self.w_meter10,
                'w_multiplier1': self.w_multiplier1,
                'w_multiplier2': self.w_multiplier2,
                'w_multiplier3': self.w_multiplier3,
                'w_multiplier4': self.w_multiplier4,
                'w_multiplier5': self.w_multiplier5,
                'w_multiplier6': self.w_multiplier6,
                'w_multiplier7': self.w_multiplier7,
                'w_multiplier8': self.w_multiplier8,
                'w_multiplier9': self.w_multiplier9,
                'w_multiplier10': self.w_multiplier10,
                'type_doble': self.type_doble,
                'humidity': self.humidity,
                }


class VisualInspectionTest(db.Model):
    """ Visual inspection test result """
    __tablename__ = u'visual_inspection_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='visual_inspection_test')
    notes = db.Column(db.String(1000))

    # Tank subgroup
    tank_cover_gasket_id = db.Column(db.Integer, db.ForeignKey("gasket_condition.id"))  # TankCoverGasket
    tank_manhole_gasket_id = db.Column(db.Integer, db.ForeignKey("gasket_condition.id"))  # TankManHole
    tank_gas_relay_id = db.Column(db.Integer, db.ForeignKey("gas_relay.id"))  # TankGasRelay
    tank_oil_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))  # TankLevel
    tank_winding_temp_max = db.Column(db.Float(10))  # TankWindingTemp
    tank_winding_temp_actual = db.Column(db.Float(10))  # TankWindingTemp2
    tank_oil_temp_max = db.Column(db.Float(10))  # TankOilTemp
    tank_oil_temp_actual = db.Column(db.Float(10))  # TankOilTemp2
    tank_winding_flag = db.Column(db.Boolean)  # TankVent
    tank_oil_flag = db.Column(db.Boolean)  # TankHeatings
    tank_pressure_unit_id = db.Column(db.Integer, db.ForeignKey("pressure_unit.id"))  # TankPressureUnit
    tank_pressure = db.Column(db.Float(10))  # TankPressure
    tank_overpressure_valve_id = db.Column(db.Integer, db.ForeignKey("valve_condition.id"))  # TankOverPressureValve
    tank_ampling_valve_id = db.Column(db.Integer, db.ForeignKey("valve_condition.id"))  # TankSamplingValve
    tank_oil_pump_id = db.Column(db.Integer, db.ForeignKey("pump_condition.id"))  # TankOilPump
    tank_gas_analyser = db.Column(db.Float(10))  # TankGasSensor
    tank_overall_condition_id = db.Column(db.Integer, db.ForeignKey("overall_condition.id"))  # TankPaint

    # Expansion/Conservator tank subgroup
    exp_tank_pipe_gasket_id = db.Column(db.Integer, db.ForeignKey("gasket_condition.id"))  # ExpTankPipeGasket
    exp_tank_oil_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))  # ExpTankLevel
    exp_tank_paint_id = db.Column(db.Integer, db.ForeignKey("paint_types.id"))  # ExpTankPaint
    exp_tank_overall_condition_id = db.Column(db.Integer, db.ForeignKey("overall_condition.id"))  # ExpTankDessicant

    # Bushing + arrester subgroup
    bushing_gasket_id = db.Column(db.Integer, db.ForeignKey("gasket_condition.id"))  # BushingGasket
    bushing_oil_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))  # BushingLevel
    bushing_overall_condition_id = db.Column(db.Integer, db.ForeignKey("overall_condition.id"))  # BushingCleaniness

    # Tap changer subgroup
    tap_changer_gasket_id = db.Column(db.Integer, db.ForeignKey("gasket_condition.id"))  # TCGasket
    tap_changer_oil_level_id = db.Column(db.Integer, db.ForeignKey("fluid_level.id"))  # TCLevel
    tap_changer_temp_max = db.Column(db.Float(10))  # TCTemperature
    tap_changer_temp_actual = db.Column(db.Float(10))  # TCTemperature2
    tap_changer_pressure_max = db.Column(db.Float(10))  # TCPressure
    tap_changer_pressure_actual = db.Column(db.Float(10))  # TCPressure2
    tap_changer_pressure_unit_id = db.Column(db.Integer, db.ForeignKey("pressure_unit.id"))  # TCPressureUnit
    tap_changer_tap_position = db.Column(db.Float(10))  # TCTapPosition
    tap_changer_overpressure_valve_id = db.Column(db.Integer, db.ForeignKey("valve_condition.id"))  # TCOverPressureValve
    tap_changer_ampling_valve_id = db.Column(db.Integer, db.ForeignKey("valve_condition.id"))  # TCSamplingGasket
    tap_changer_operation_counter = db.Column(db.Integer)  # TCOperationCounter
    tap_changer_counter_id = db.Column(db.Integer, db.ForeignKey("tap_counter_status.id"))  # TCCounter
    tap_changer_filter_id = db.Column(db.Integer, db.ForeignKey("tap_filter_condition.id"))  # TCFilter
    tap_changer_overall_condition_id = db.Column(db.Integer, db.ForeignKey("overall_condition.id"))  # TCPaint

    # Radiator subgroup
    radiator_fan_id = db.Column(db.Integer, db.ForeignKey("fan_condition.id"))  # RadiatorFan
    radiator_gasket_id = db.Column(db.Integer, db.ForeignKey("gasket_condition.id"))  # RadiatorGasket
    radiator_overall_condition_id = db.Column(db.Integer, db.ForeignKey("overall_condition.id"))  # RadiatorGeneralCondition

    # Control cabinet subgroup
    control_cab_connection_id = db.Column(db.Integer, db.ForeignKey("connection_condition.id"))  # PhaseElectricalConnection
    control_cab_heating_id = db.Column(db.Integer, db.ForeignKey("heating_condition.id"))  # SSIndicator
    control_cab_overall_condition_id = db.Column(db.Integer, db.ForeignKey("overall_condition.id"))  # PhaseGeneralCondition

    # Grounding
    grounding_value = db.Column(db.Float(53))  # GroundingValue
    grounding_connection_id = db.Column(db.Integer, db.ForeignKey("connection_condition.id"))  # GroundingConnection

    # Miscellaneous
    misc_foundation_id = db.Column(db.Integer, db.ForeignKey("foundation_condition.id"))  # foundation_condition
    misc_temp_ambiant = db.Column(db.Float(53))  # AmbiantTemperature
    misc_load = db.Column(db.Float(53))  # Load

    # Cuve_Temp_Bob_Decl1 = db.Column(db.Float(53))#TankTemperatureWindingTrip1
    # Cuve_Temp_Bob_Decl2 = db.Column(db.Float(53))#TankTemperatureWindingTrip2
    # Cuve_Temp_Bob_Decl3 = db.Column(db.Float(53))#TankTemperatureWindingTrip4
    # Cuve_Temp_Liq_Decl1 = db.Column(db.Float(53))#TankTemperatureOilTrip1
    # Cuve_Temp_Liq_Decl2 = db.Column(db.Float(53))#TankTemperatureOilTrip2
    # Cuve_Temp_Liq_Decl3 = db.Column(db.Float(53))#TankTemperatureOilTrip3
    # Cuve_TempContact_Bob_Decl1 = db.Column(db.Boolean)#TankTemperatureContactWindingTrip1
    # Cuve_TempContact_Liq_Decl1 = db.Column(db.Boolean)#TankTemperatureContactOilTrip11

    # relationships
    tank_cover_gasket = db.relationship('GasketCondition', foreign_keys='VisualInspectionTest.tank_cover_gasket_id')
    tank_manhole_gasket = db.relationship('GasketCondition', foreign_keys='VisualInspectionTest.tank_manhole_gasket_id')
    tank_gas_relay = db.relationship('GasRelay', foreign_keys='VisualInspectionTest.tank_gas_relay_id')
    tank_oil_level = db.relationship('FluidLevel', foreign_keys='VisualInspectionTest.tank_oil_level_id')
    tank_pressure_unit = db.relationship('PressureUnit', foreign_keys='VisualInspectionTest.tank_pressure_unit_id')
    tank_overpressure_valve = db.relationship('ValveCondition', foreign_keys='VisualInspectionTest.tank_overpressure_valve_id')
    tank_ampling_valve = db.relationship('ValveCondition', foreign_keys='VisualInspectionTest.tank_ampling_valve_id')
    tank_oil_pump = db.relationship('PumpCondition', foreign_keys='VisualInspectionTest.tank_oil_pump_id')
    tank_overall_condition = db.relationship('OverallCondition', foreign_keys='VisualInspectionTest.tank_overall_condition_id')
    exp_tank_pipe_gasket = db.relationship('GasketCondition', foreign_keys='VisualInspectionTest.exp_tank_pipe_gasket_id')
    exp_tank_oil_level = db.relationship('FluidLevel', foreign_keys='VisualInspectionTest.exp_tank_oil_level_id')
    exp_tank_paint = db.relationship('PaintTypes', foreign_keys='VisualInspectionTest.exp_tank_paint_id')
    exp_tank_overall_condition = db.relationship('OverallCondition', foreign_keys='VisualInspectionTest.exp_tank_overall_condition_id')
    bushing_gasket = db.relationship('GasketCondition', foreign_keys='VisualInspectionTest.bushing_gasket_id')
    bushing_oil_level = db.relationship('FluidLevel', foreign_keys='VisualInspectionTest.bushing_oil_level_id')
    bushing_overall_condition = db.relationship('OverallCondition', foreign_keys='VisualInspectionTest.bushing_overall_condition_id')
    tap_changer_gasket = db.relationship('GasketCondition', foreign_keys='VisualInspectionTest.tap_changer_gasket_id')
    tap_changer_oil_level = db.relationship('FluidLevel', foreign_keys='VisualInspectionTest.tap_changer_oil_level_id')
    tap_changer_pressure_unit = db.relationship('PressureUnit', foreign_keys='VisualInspectionTest.tap_changer_pressure_unit_id')
    tap_changer_overpressure_valve = db.relationship('ValveCondition', foreign_keys='VisualInspectionTest.tap_changer_overpressure_valve_id')
    tap_changer_ampling_valve = db.relationship('ValveCondition', foreign_keys='VisualInspectionTest.tap_changer_ampling_valve_id')
    tap_changer_counter = db.relationship('TapCounterStatus', foreign_keys='VisualInspectionTest.tap_changer_counter_id')
    tap_changer_filter = db.relationship('TapFilterCondition', foreign_keys='VisualInspectionTest.tap_changer_filter_id')
    tap_changer_overall_condition = db.relationship('OverallCondition', foreign_keys='VisualInspectionTest.tap_changer_overall_condition_id')
    radiator_fan = db.relationship('FanCondition', foreign_keys='VisualInspectionTest.radiator_fan_id')
    radiator_gasket = db.relationship('GasketCondition', foreign_keys='VisualInspectionTest.radiator_gasket_id')
    radiator_overall_condition = db.relationship('OverallCondition', foreign_keys='VisualInspectionTest.radiator_overall_condition_id')
    control_cab_connection = db.relationship('ConnectionCondition', foreign_keys='VisualInspectionTest.control_cab_connection_id')
    control_cab_heating = db.relationship('HeatingCondition', foreign_keys='VisualInspectionTest.control_cab_heating_id')
    control_cab_overall_condition = db.relationship('OverallCondition', foreign_keys='VisualInspectionTest.control_cab_overall_condition_id')
    grounding_connection = db.relationship('ConnectionCondition', foreign_keys='VisualInspectionTest.grounding_connection_id')
    misc_foundation = db.relationship('FoundationCondition', foreign_keys='VisualInspectionTest.misc_foundation_id')

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'notes': self.notes,
                'tank_cover_gasket_id': self.tank_cover_gasket_id,
                'tank_manhole_gasket_id': self.tank_manhole_gasket_id,
                'tank_gas_relay_id': self.tank_gas_relay_id,
                'tank_oil_level_id': self.tank_oil_level_id,
                'tank_winding_temp_max': self.tank_winding_temp_max,
                'tank_winding_temp_actual': self.tank_winding_temp_actual,
                'tank_oil_temp_max': self.tank_oil_temp_max,
                'tank_oil_temp_actual': self.tank_oil_temp_actual,
                'tank_winding_flag': self.tank_winding_flag,
                'tank_oil_flag': self.tank_oil_flag,
                'tank_pressure_unit_id': self.tank_pressure_unit_id,
                'tank_pressure': self.tank_pressure,
                'tank_overpressure_valve_id': self.tank_overpressure_valve_id,
                'tank_ampling_valve_id': self.tank_ampling_valve_id,
                'tank_oil_pump_id': self.tank_oil_pump_id,
                'tank_gas_analyser': self.tank_gas_analyser,
                'tank_overall_condition_id': self.tank_overall_condition_id,
                'exp_tank_pipe_gasket_id': self.exp_tank_pipe_gasket_id,
                'exp_tank_oil_level_id': self.exp_tank_oil_level_id,
                'exp_tank_paint_id': self.exp_tank_paint_id,
                'exp_tank_overall_condition_id': self.exp_tank_overall_condition_id,
                'bushing_gasket_id': self.bushing_gasket_id,
                'bushing_oil_level_id': self.bushing_oil_level_id,
                'bushing_overall_condition_id': self.bushing_overall_condition_id,
                'tap_changer_gasket_id': self.tap_changer_gasket_id,
                'tap_changer_oil_level_id': self.tap_changer_oil_level_id,
                'tap_changer_temp_max': self.tap_changer_temp_max,
                'tap_changer_temp_actual': self.tap_changer_temp_actual,
                'tap_changer_pressure_max': self.tap_changer_pressure_max,
                'tap_changer_pressure_actual': self.tap_changer_pressure_actual,
                'tap_changer_pressure_unit_id': self.tap_changer_pressure_unit_id,
                'tap_changer_tap_position': self.tap_changer_tap_position,
                'tap_changer_overpressure_valve_id': self.tap_changer_overpressure_valve_id,
                'tap_changer_ampling_valve_id': self.tap_changer_ampling_valve_id,
                'tap_changer_operation_counter': self.tap_changer_operation_counter,
                'tap_changer_counter_id': self.tap_changer_counter_id,
                'tap_changer_filter_id': self.tap_changer_filter_id,
                'tap_changer_overall_condition_id': self.tap_changer_overall_condition_id,
                'radiator_fan_id': self.radiator_fan_id,
                'radiator_gasket_id': self.radiator_gasket_id,
                'radiator_overall_condition_id': self.radiator_overall_condition_id,
                'control_cab_connection_id': self.control_cab_connection_id,
                'control_cab_heating_id': self.control_cab_heating_id,
                'control_cab_overall_condition_id': self.control_cab_overall_condition_id,
                'grounding_value': self.grounding_value,
                'grounding_connection_id': self.grounding_connection_id,
                'misc_foundation_id': self.misc_foundation_id,
                'misc_temp_ambiant': self.misc_temp_ambiant,
                'misc_load': self.misc_load,
                'tank_cover_gasket': self.tank_cover_gasket and self.tank_cover_gasket.serialize(),
                'tank_manhole_gasket': self.tank_manhole_gasket and self.tank_manhole_gasket.serialize(),
                'tank_gas_relay': self.tank_gas_relay and self.tank_gas_relay.serialize(),
                'tank_oil_level': self.tank_oil_level and self.tank_oil_level.serialize(),
                'tank_pressure_unit': self.tank_pressure_unit and self.tank_pressure_unit.serialize(),
                'tank_overpressure_valve': self.tank_overpressure_valve and self.tank_overpressure_valve.serialize(),
                'tank_ampling_valve': self.tank_ampling_valve and self.tank_ampling_valve.serialize(),
                'tank_oil_pump': self.tank_oil_pump and self.tank_oil_pump.serialize(),
                'tank_overall_condition': self.tank_overall_condition and self.tank_overall_condition.serialize(),
                'exp_tank_pipe_gasket': self.exp_tank_pipe_gasket and self.exp_tank_pipe_gasket.serialize(),
                'exp_tank_oil_level': self.exp_tank_oil_level and self.exp_tank_oil_level.serialize(),
                'exp_tank_paint': self.exp_tank_paint and self.exp_tank_paint.serialize(),
                'exp_tank_overall_condition': self.exp_tank_overall_condition and self.exp_tank_overall_condition.serialize(),
                'bushing_gasket': self.bushing_gasket and self.bushing_gasket.serialize(),
                'bushing_oil_level': self.bushing_oil_level and self.bushing_oil_level.serialize(),
                'bushing_overall_condition': self.bushing_overall_condition and self.bushing_overall_condition.serialize(),
                'tap_changer_gasket': self.tap_changer_gasket and self.tap_changer_gasket.serialize(),
                'tap_changer_oil_level': self.tap_changer_oil_level and self.tap_changer_oil_level.serialize(),
                'tap_changer_pressure_unit': self.tap_changer_pressure_unit and self.tap_changer_pressure_unit.serialize(),
                'tap_changer_overpressure_valve': self.tap_changer_overpressure_valve and self.tap_changer_overpressure_valve.serialize(),
                'tap_changer_ampling_valve': self.tap_changer_ampling_valve and self.tap_changer_ampling_valve.serialize(),
                'tap_changer_counter': self.tap_changer_counter and self.tap_changer_counter.serialize(),
                'tap_changer_filter': self.tap_changer_filter and self.tap_changer_filter.serialize(),
                'tap_changer_overall_condition': self.tap_changer_overall_condition and self.tap_changer_overall_condition.serialize(),
                'radiator_fan': self.radiator_fan and self.radiator_fan.serialize(),
                'radiator_gasket': self.radiator_gasket and self.radiator_gasket.serialize(),
                'radiator_overall_condition': self.radiator_overall_condition and self.radiator_overall_condition.serialize(),
                'control_cab_connection': self.control_cab_connection and self.control_cab_connection.serialize(),
                'control_cab_heating': self.control_cab_heating and self.control_cab_heating.serialize(),
                'control_cab_overall_condition': self.control_cab_overall_condition and self.control_cab_overall_condition.serialize(),
                'grounding_connection': self.grounding_connection and self.grounding_connection.serialize(),
                'misc_foundation': self.misc_foundation and self.misc_foundation.serialize(),
                }


class InsulationResistanceTest(db.Model):
    __tablename__ = u'insulation_resistance_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='insulation_resistance_test')
    test_kv1 = db.Column(db.Float(53))
    resistance1 = db.Column(db.Float(53))  # in megohm
    multiplier1 = db.Column(db.Float(53))
    test_kv2 = db.Column(db.Float(53))
    resistance2 = db.Column(db.Float(53))  # in megohm
    multiplier2 = db.Column(db.Float(53))
    test_kv3 = db.Column(db.Float(53))
    resistance3 = db.Column(db.Float(53))  # in megohm
    multiplier3 = db.Column(db.Float(53))
    test_kv4 = db.Column(db.Float(53))
    resistance4 = db.Column(db.Float(53))  # in megohm
    multiplier4 = db.Column(db.Float(53))
    test_kv5 = db.Column(db.Float(53))
    resistance5 = db.Column(db.Float(53))  # in megohm
    multiplier5 = db.Column(db.Float(53))

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'test_kv1': self.test_kv1,
                'resistance1': self.resistance1,
                'multiplier1': self.multiplier1,
                'test_kv2': self.test_kv2,
                'resistance2': self.resistance2,
                'multiplier2': self.multiplier2,
                'test_kv3': self.test_kv3,
                'resistance3': self.resistance3,
                'multiplier3': self.multiplier3,
                'test_kv4': self.test_kv4,
                'resistance4': self.resistance4,
                'multiplier4': self.multiplier4,
                'test_kv5': self.test_kv5,
                'resistance5': self.resistance5,
                'multiplier5': self.multiplier5,
                }


class PolymerisationDegreeTest(db.Model):
    """DP. Degree of polymerisation of paper results"""
    __tablename__ = u'polymerisation_degree_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='polymerisation_degree_test')
    phase_a1 = db.Column(db.Float(53))  # Remaining are equivalent
    phase_a2 = db.Column(db.Float(53))
    phase_a3 = db.Column(db.Float(53))
    phase_b1 = db.Column(db.Float(53))
    phase_b2 = db.Column(db.Float(53))
    phase_b3 = db.Column(db.Float(53))
    phase_c1 = db.Column(db.Float(53))
    phase_c2 = db.Column(db.Float(53))
    phase_c3 = db.Column(db.Float(53))
    lead_a = db.Column(db.Numeric(4))
    lead_b = db.Column(db.Numeric(4))
    lead_c = db.Column(db.Numeric(4))
    lead_n = db.Column(db.Numeric(4))
    winding = db.Column(db.Numeric(4))

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'phase_a1': self.phase_a1,
                'phase_a2': self.phase_a2,
                'phase_a3': self.phase_a3,
                'phase_b1': self.phase_b1,
                'phase_b2': self.phase_b2,
                'phase_b3': self.phase_b3,
                'phase_c1': self.phase_c1,
                'phase_c2': self.phase_c2,
                'phase_c3': self.phase_c3,
                'lead_a': self.lead_a,
                'lead_b': self.lead_b,
                'lead_c': self.lead_c,
                'lead_n': self.lead_n,
                'winding': self.winding,
                }


class TransformerTurnRatioTest(db.Model):
    """TTR.  Transformer Turn Ratio test result
     It could by more then one string of TTR related with one test_result"""
    __tablename__ = u'transformer_turn_ratio_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='transformer_turn_ratio_test')
    winding = db.Column(db.Integer, nullable=False)  # Winding. Winding, primary, secondary, etc. been measured
    tap_position = db.Column(db.Integer)  # Tap position.
    measured_current1 = db.Column(db.Float(53))  # Measured ratio of phase 1
    measured_current2 = db.Column(db.Float(53))  # Measured ratio of phase 2
    measured_current3 = db.Column(db.Float(53))  # Measured ratio of phase 3
    calculated_current1 = db.Column(db.Float(53))  # Measured excitation current phase 1
    calculated_current2 = db.Column(db.Float(53))  # Measured excitation current phase 2
    calculated_current3 = db.Column(db.Float(53))  # Measured excitation current phase 3
    error1 = db.Column(db.Float(53))  # Ratio error between calculated and measured on phase 1
    error2 = db.Column(db.Float(53))  # Ratio error between calculated and measured on phase 2
    error3 = db.Column(db.Float(53))  # Ratio error between calculated and measured on phase 3
    ratio = db.Column(db.Float(53))  # Calculated ratio
    select = db.Column(db.Boolean)  # TapPos. Tap position during normal operation.

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'winding': self.winding,
                'tap_position': self.tap_position,
                'measured_current1': self.measured_current1,
                'measured_current2': self.measured_current2,
                'measured_current3': self.measured_current3,
                'calculated_current1': self.calculated_current1,
                'calculated_current2': self.calculated_current2,
                'calculated_current3': self.calculated_current3,
                'error1': self.error1,
                'error2': self.error2,
                'error3': self.error3,
                'ratio': self.ratio,
                'select': self.select,
                }


class WindingResistanceTest(db.Model):
    """WindingResistanceTest.  Resistance; winding/contact. Winding resistance test results.
    It could by more then one string of winding resistance related with one test_result"""
    __tablename__ = u'winding_resistance_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='winding_resistance_test')
    winding = db.Column(db.Integer, nullable=False)  # Winding. Winding, primary, secondary, etc. been measured
    tap_position = db.Column(db.Integer)  # Tap position.
    mesure1 = db.Column(db.Float(53))  # Measure1
    temp1 = db.Column(db.Float(53))  # Temperature1. In Celsius
    corr1 = db.Column(db.Float(53))  # Correction1
    mesure2 = db.Column(db.Float(53))  # Measure2
    temp2 = db.Column(db.Float(53))  # Temperature2
    corr2 = db.Column(db.Float(53))  # Correction2
    mesure3 = db.Column(db.Float(53))  # Measure3
    temp3 = db.Column(db.Float(53))  # Temperature3
    corr3 = db.Column(db.Float(53))  # Correction3

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'winding': self.winding,
                'tap_position': self.tap_position,
                'mesure1': self.mesure1,
                'temp1': self.temp1,
                'corr1': self.corr1,
                'mesure2': self.mesure2,
                'temp2': self.temp2,
                'corr2': self.corr2,
                'mesure3': self.mesure3,
                'temp3': self.temp3,
                'corr3': self.corr3,
                }


class DissolvedGasTest(db.Model):
    """DissolvedGasTest. Dissolved gas results.
    We should add sub-table to store results to specific online gas sensor,
    such as Kelman acoustic sensor data.
    """
    __tablename__ = u'dissolved_gas_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='dissolved_gas_test')
    h2 = db.Column(db.Float(53))  # H2, Hydrogen (ppm)
    o2 = db.Column(db.Float(53))  # O2, Oxygen (ppm)
    n2 = db.Column(db.Float(53))  # N2, Nitrogen (ppm)
    co = db.Column(db.Float(53))  # CO, Carbon monoxide (ppm)
    ch4 = db.Column(db.Float(53))  # CH4, Methane (ppm)
    co2 = db.Column(db.Float(53))  # CO2, Carbon dioxide (ppm)
    c2h2 = db.Column(db.Float(53))  # C2H2, Acetylene (ppm)
    c2h4 = db.Column(db.Float(53))  # C2H4, Ethylene (ppm)
    c2h6 = db.Column(db.Float(53))  # C2H6, Ethane (ppm)
    h2_flag = db.Column(db.Boolean)  # true if not detectable
    o2_flag = db.Column(db.Boolean)  # true if not detectable
    n2_flag = db.Column(db.Boolean)  # true if not detectable
    co_flag = db.Column(db.Boolean)  # true if not detectable
    ch4_flag = db.Column(db.Boolean)  # true if not detectable
    co2_flag = db.Column(db.Boolean)  # true if not detectable
    c2h2_flag = db.Column(db.Boolean)  # true if not detectable
    c2h4_flag = db.Column(db.Boolean)  # true if not detectable
    c2h6_flag = db.Column(db.Boolean)  # true if not detectable
    cap_gaz = db.Column(db.Float(53))  # GasSensor, value of gas sensor at time of sampling
    content_gaz = db.Column(db.Float(53))  # TCG. Total Gas content
    # Noise = db.Column(db.Float(53))             #Kelman acoustic sensor
    # Tzone1 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # Tzone2 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # Flow_gas = db.Column(db.Float(53)           #Kelman acoustic sensor
    # Pcell = db.Column(db.Float(53))             #Kelman acoustic sensor
    # Toil_hs = db.Column(db.Float(53)            #Kelman acoustic sensor
    # Tpga = db.Column(db.Float(53))              #Kelman acoustic sensor
    # RH_pga = db.Column(db.Float(53)             #Kelman acoustic sensor
    # Normalization_Temperature = db.Column(db.Float(53))#Kelman acoustic sensor
    # Oil_Pressure = db.Column(db.Float(53))      #Kelman acoustic sensor
    # Poil_pump = db.Column(db.Float(53))         #Kelman acoustic sensor
    # Toil_cond = db.Column(db.Float(53))         #Kelman acoustic sensor
    # Oil_Temperature = db.Column(db.Float(53))   #Kelman acoustic sensor
    # N_fill = db.Column(db.Float(53))            #Kelman acoustic sensor
    # N_drain = db.Column(db.Float(53))           #Kelman acoustic sensor
    # Mic1 = db.Column(db.Float(53))              #Kelman acoustic sensor
    # Mic2 = db.Column(db.Float(53))              #Kelman acoustic sensor
    # opt_36 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_37 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_38 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_39 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_40 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_41 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_42 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_43 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_44 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_45 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_46 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_47 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_48 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_49 = db.Column(db.Float(53))            #Kelman acoustic sensor
    # opt_50 = db.Column(db.Float(53))            #Kelman acoustic sensor

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'h2': self.h2,
                'o2': self.o2,
                'n2': self.n2,
                'co': self.co,
                'ch4': self.ch4,
                'co2': self.co2,
                'c2h2': self.c2h2,
                'c2h4': self.c2h4,
                'c2h6': self.c2h6,
                'h2_flag': self.h2_flag,
                'o2_flag': self.o2_flag,
                'n2_flag': self.n2_flag,
                'co_flag': self.co_flag,
                'ch4_flag': self.ch4_flag,
                'co2_flag': self.co2_flag,
                'c2h2_flag': self.c2h2_flag,
                'c2h4_flag': self.c2h4_flag,
                'c2h6_flag': self.c2h6_flag,
                'cap_gaz': self.cap_gaz,
                'content_gaz': self.content_gaz,
                }


class WaterTest(db.Model):
    """Water. Dissolved and free water content in oil test results"""
    __tablename__ = u'water_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='water_test')
    water_flag = db.Column(db.Boolean)  # FreeWater. Indicates if free water is present.
    water = db.Column(db.Float(53))  # Water. Dissolved water content in the insulated fluid
    remark = db.Column(db.String(80))  # Remark.

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'water_flag': self.water_flag,
                'water': self.water,
                'remark': self.remark
                }


class FuranTest(db.Model):
    """FuranTest.  Furan test results."""
    __tablename__ = u'furan_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='furan_test')
    hmf = db.Column(db.Float(53))  # HMF, Hydroxymethylfurfural test in ppm
    fol = db.Column(db.Float(53))  # FOL, Furfurol
    fal = db.Column(db.Float(53))  # FAL, Furfural
    acf = db.Column(db.Float(53))  # ACF, Acetyl Furan
    mef = db.Column(db.Float(53))  # MEF, Methyl furan
    hmf_flag = db.Column(db.Boolean)  # HMF flag, true if not detectable
    fol_flag = db.Column(db.Boolean)  # FOL flag, true if not detectable
    fal_flag = db.Column(db.Boolean)  # FAL flag, true if not detectable
    acf_flag = db.Column(db.Boolean)  # ACF flag, true if not detectable
    mef_flag = db.Column(db.Boolean)  # MEF flag, true if not detectable

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'hmf': self.hmf,
                'fol': self.fol,
                'fal': self.fal,
                'acf': self.acf,
                'mef': self.mef,
                'hmf_flag': self.hmf_flag,
                'fol_flag': self.fol_flag,
                'fal_flag': self.fal_flag,
                'acf_flag': self.acf_flag,
                'mef_flag': self.mef_flag,
                }


class InhibitorTest(db.Model):
    """DPCB results. InhibitorTest. AntioxidantTest"""
    __tablename__ = u'inhibitor_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='inhibitor_test')
    inhibitor_type_id = db.Column(db.Integer, db.ForeignKey("inhibitor_type.id"))
    inhibitor_type = db.relationship('InhibitorType', foreign_keys='InhibitorTest.inhibitor_type_id')

    inhibitor = db.Column(db.Float(53))  # Remaining are equivalent
    remark = db.Column(db.String(80))
    inhibitor_flag = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'inhibitor_type_id': self.inhibitor_type_id,
                'inhibitor_type': self.inhibitor_type and self.inhibitor_type.serialize(),
                'inhibitor': self.inhibitor,
                'remark': self.remark,
                'inhibitor_flag': self.inhibitor_flag,
                }


class InhibitorType(db.Model):
    """Inhibitor types database"""
    __tablename__ = u'inhibitor_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name}


class PCBTest(db.Model):
    """PCBTest fluid test results"""
    __tablename__ = u'pcb_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='pcb_test')
    aroclor_1242 = db.Column(db.Float(53))  # Remaining are equivalent
    aroclor_1254 = db.Column(db.Float(53))
    aroclor_1260 = db.Column(db.Float(53))
    aroclor_1242_flag = db.Column(db.Boolean)
    aroclor_1254_flag = db.Column(db.Boolean)
    aroclor_1260_flag = db.Column(db.Boolean)
    pcb_total = db.Column(db.Float(53))
    total_flag = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'aroclor_1242': self.aroclor_1242,
                'aroclor_1254': self.aroclor_1254,
                'aroclor_1260': self.aroclor_1260,
                'aroclor_1242_flag': self.aroclor_1242_flag,
                'aroclor_1254_flag': self.aroclor_1254_flag,
                'aroclor_1260_flag': self.aroclor_1260_flag,
                'pcb_total': self.pcb_total,
                'total_flag': self.total_flag,
                }


class ParticleTest(db.Model):
    """ParticleTest. Number and sized of particles found in the fluid """
    __tablename__ = u'particle_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='particle_test')
    _2um = db.Column(u'2um', db.Float(53))  # _2um
    _5um = db.Column(u'5um', db.Float(53))  # _5um
    _10um = db.Column(u'10um', db.Float(53))  # _10um
    _15um = db.Column(u'15um', db.Float(53))  # _15um
    _25um = db.Column(u'25um', db.Float(53))  # _25um
    _50um = db.Column(u'50um', db.Float(53))  # _50um
    _100um = db.Column(u'100um', db.Float(53))  # _100um
    nas1638 = db.Column(db.Float(53))  # NAS1638
    iso4406_1 = db.Column(db.Float(53))  # ISO4406_1
    iso4406_2 = db.Column(db.Float(53))  # ISO4406_2
    iso4406_3 = db.Column(db.Float(53))  # ISO4406_3

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                '_2um': self._2um,
                '_5um': self._5um,
                '_10um': self._10um,
                '_15um': self._15um,
                '_25um': self._25um,
                '_50um': self._50um,
                '_100um': self._100um,
                'nas1638': self.nas1638,
                'iso4406_1': self.iso4406_1,
                'iso4406_2': self.iso4406_2,
                'iso4406_3': self.iso4406_3,
                }


class MetalsInOilTest(db.Model):
    """MetalInFluid. Dissolved metal in insulated fluid test results."""
    __tablename__ = u'metals_in_oil_test'

    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='metals_in_oil_test')
    iron = db.Column(db.Float(53))  # Iron
    nickel = db.Column(db.Float(53))  # Nickel
    aluminium = db.Column(db.Float(53))  # Aluminium
    copper = db.Column(db.Float(53))  # Copper
    tin = db.Column(db.Float(53))  # Tin
    silver = db.Column(db.Float(53))  # Silver
    lead = db.Column(db.Float(53))  # Lead
    zinc = db.Column(db.Float(53))  # Zinc
    arsenic = db.Column(db.Float(53))
    cadmium = db.Column(db.Float(53))
    chrome = db.Column(db.Float(53))
    iron_flag = db.Column(
        db.Boolean)  # bAluminium. Boolean are used to indicate non detectable concentration rather than use 0
    nickel_flag = db.Column(db.Boolean)  # bIron
    aluminium_flag = db.Column(db.Boolean)  # bTin
    copper_flag = db.Column(db.Boolean)  # bZinc
    tin_flag = db.Column(db.Boolean)  # bNickel
    silver_flag = db.Column(db.Boolean)  # bSilver
    lead_flag = db.Column(db.Boolean)  # bLead
    zinc_flag = db.Column(db.Boolean)  # bCopperarsenic
    arsenic_flag = db.Column(db.Boolean)
    cadmium_flag = db.Column(db.Boolean)
    chrome_flag = db.Column(db.Boolean)

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'iron': self.iron,
                'nickel': self.nickel,
                'aluminium': self.aluminium,
                'copper': self.copper,
                'tin': self.tin,
                'silver': self.silver,
                'lead': self.lead,
                'zinc': self.zinc,
                'arsenic': self.arsenic,
                'cadmium': self.cadmium,
                'chrome': self.chrome,
                'iron_flag': self.iron_flag,
                'nickel_flag': self.nickel_flag,
                'aluminium_flag': self.aluminium_flag,
                'copper_flag': self.copper_flag,
                'tin_flag': self.tin_flag,
                'silver_flag': self.silver_flag,
                'lead_flag': self.lead_flag,
                'zinc_flag': self.zinc_flag,
                'arsenic_flag': self.arsenic_flag,
                'cadmium_flag': self.cadmium_flag,
                'chrome_flag': self.chrome_flag,
                }


class FluidTest(db.Model):
    """PHY. Fluid physical properties test results"""
    __tablename__ = u'fluid_test'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', backref='fluid_test')
    dielectric_1816 = db.Column(db.Float(53))  # D1816
    dielectric_1816_2 = db.Column(db.Float(53))  # D1816_2
    dielectric_877 = db.Column(db.Float(53))  # D877
    dielectric_iec_156 = db.Column(db.Float(53))  # CEI156
    acidity = db.Column(db.Float(53))  # Acid
    color = db.Column(db.Float(53))  # Color
    ift = db.Column(db.Float(53))  # IFT
    visual = db.Column(db.String(25))  # Visual
    density = db.Column(db.Float(53))  # Density
    pf20c = db.Column(db.Float(53))  # PF20C
    pf100c = db.Column(db.Float(53))  # PF100C
    sludge = db.Column(db.Float(53))  # Sludge
    aniline_point = db.Column(db.Float(53))  # AnilinePoint
    corrosive_sulfur = db.Column(db.String(25))  # CorrosiveSulfur
    viscosity = db.Column(db.Float(53))  # Viscosity
    flash_point = db.Column(db.Float(53))  # FlashPoint
    pour_point = db.Column(db.Float(53))  # PourPoint
    dielectric_1816_flag = db.Column(db.Boolean)  # b1816
    dielectric_1816_2_flag = db.Column(db.Boolean)  # bD1816_2
    dielectric_877_flag = db.Column(db.Boolean)  # bD877
    dielectric_iec_156_flag = db.Column(db.Boolean)  # bCEI156

    def __repr__(self):
        return "{} {}".format(self.id, self.test_result)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'dielectric_1816': self.dielectric_1816,
                'dielectric_1816_2': self.dielectric_1816_2,
                'dielectric_877': self.dielectric_877,
                'dielectric_iec_156': self.dielectric_iec_156,
                'acidity': self.acidity,
                'color': self.color,
                'ift': self.ift,
                'visual': self.visual,
                'density': self.density,
                'pf20c': self.pf20c,
                'pf100c': self.pf100c,
                'sludge': self.sludge,
                'aniline_point': self.aniline_point,
                'corrosive_sulfur': self.corrosive_sulfur,
                'viscosity': self.viscosity,
                'flash_point': self.flash_point,
                'pour_point': self.pour_point,
                'dielectric_1816_flag': self.dielectric_1816_flag,
                'dielectric_1816_2_flag': self.dielectric_1816_2_flag,
                'dielectric_877_flag': self.dielectric_877_flag,
                'dielectric_iec_156_flag': self.dielectric_iec_156_flag,
                }


class NormPhysic(db.Model):

    __tablename__ = 'norm_physic'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False, index=True)
    equipment_id = db.Column(db.Integer, nullable=False)
    acid_min = db.Column(db.Float(53))
    acid_max = db.Column(db.Float(53))
    ift_min = db.Column(db.Float(53))
    ift_max = db.Column(db.Float(53))
    d1816_min = db.Column(db.Float(53))
    d1816_max = db.Column(db.Float(53))
    d877_min = db.Column(db.Float(53))
    d877_max = db.Column(db.Float(53))
    color_min = db.Column(db.Float(53))
    color_max = db.Column(db.Float(53))
    density_min = db.Column(db.Float(53))
    density_max = db.Column(db.Float(53))
    pf20_min = db.Column(db.Float(53))
    pf20_max = db.Column(db.Float(53))
    water_min = db.Column(db.Float(53))
    water_max = db.Column(db.Float(53))
    flashpoint_min = db.Column(db.Float(53))
    flashpoint_max = db.Column(db.Float(53))
    pourpoint_min = db.Column(db.Float(53))
    pourpoint_max = db.Column(db.Float(53))
    viscosity_min = db.Column(db.Float(53))
    viscosity_max = db.Column(db.Float(53))
    d1816_2_min = db.Column(db.Float(53))
    d1816_2_max = db.Column(db.Float(53), server_default=db.text("0"))
    p100_min = db.Column(db.Float(53))
    p100_max = db.Column(db.Float(53))
    fluid_type_id = db.Column(db.Integer, server_default=db.text("0"))
    cei156_min = db.Column(db.Integer, server_default=db.text("0"))
    cei156_max = db.Column(db.Integer, server_default=db.text("0"))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'equipment_id': self.equipment_id,
                'acid_min': self.acid_min,
                'acid_max': self.acid_max,
                'ift_min': self.ift_min,
                'ift_max': self.ift_max,
                'd1816_min': self.d1816_min,
                'd1816_max': self.d1816_max,
                'd877_min': self.d877_min,
                'd877_max': self.d877_max,
                'color_min': self.color_min,
                'color_max': self.color_max,
                'density_min': self.density_min,
                'density_max': self.density_max,
                'pf20_min': self.pf20_min,
                'pf20_max': self.pf20_max,
                'water_min': self.water_min,
                'water_max': self.water_max,
                'flashpoint_min': self.flashpoint_min,
                'flashpoint_max': self.flashpoint_max,
                'pourpoint_min': self.pourpoint_min,
                'pourpoint_max': self.pourpoint_max,
                'viscosity_min': self.viscosity_min,
                'viscosity_max': self.viscosity_max,
                'd1816_2_min': self.d1816_2_min,
                'd1816_2_max': self.d1816_2_max,
                'p100_min': self.p100_min,
                'p100_max': self.p100_max,
                'fluid_type_id': self.fluid_type_id,
                'cei156_min': self.cei156_min,
                'cei156_max': self.cei156_max,
                }


class NormGas(db.Model):

    __tablename__ = 'norm_gas'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column('name', db.String(50), index=True)
    condition = db.Column('condition', db.Integer, server_default=db.text("0"))
    h2 = db.Column('h2', db.Float(53), server_default=db.text("0"))
    ch4 = db.Column('ch4', db.Float(53), server_default=db.text("0"))
    c2h2 = db.Column('c2h2', db.Float(53), server_default=db.text("0"))
    c2h4 = db.Column('c2h4', db.Float(53), server_default=db.text("0"))
    c2h6 = db.Column('c2h6', db.Float(53), server_default=db.text("0"))
    co = db.Column('co', db.Float(53), server_default=db.text("0"))
    co2 = db.Column('co2', db.Float(53), server_default=db.text("0"))
    tdcg = db.Column('tdcg', db.Float(53), server_default=db.text("0"))
    fluid_level = db.Column('fluid_level', db.Integer, server_default=db.text("0"))
    # db.Index('norm_gas_condition_key', 'name', 'condition', unique=True)

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'condition': self.condition,
                'h2': self.h2,
                'ch4': self.ch4,
                'c2h2': self.c2h2,
                'c2h4': self.c2h4,
                'c2h6': self.c2h6,
                'co': self.co,
                'co2': self.co2,
                'tdcg': self.tdcg,
                'fluid_level': self.fluid_level,
                }


class NormParticles(db.Model):
    __tablename__ = 'particles'

    id = db.Column(db.String(50), primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"))
    equipment = db.relationship('Equipment', foreign_keys='NormParticles.equipment_id')
    _2um = db.Column(u'2um', db.Float(53))  # _2um
    _5um = db.Column(u'5um', db.Float(53))  # _5um
    _10um = db.Column(u'10um', db.Float(53))  # _10um
    _15um = db.Column(u'15um', db.Float(53))  # _15um
    _25um = db.Column(u'25um', db.Float(53))  # _25um
    _50um = db.Column(u'50um', db.Float(53))  # _50um
    _100um = db.Column(u'100um', db.Float(53))  # _100um
    nas1638 = db.Column(db.Float(53))  # NAS1638
    iso4406_1 = db.Column(db.Float(53))  # ISO4406_1
    iso4406_2 = db.Column(db.Float(53))  # ISO4406_2
    iso4406_3 = db.Column(db.Float(53))  # ISO4406_3

    def __repr__(self):
        return self.id

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'equipment_id': self.equipment_id,
                'equipment': self.equipment and self.equipment.serialize(),
                '_2um': self._2um,
                '_5um': self._5um,
                '_10um': self._10um,
                '_15um': self._15um,
                '_25um': self._25um,
                '_50um': self._50um,
                '_100um': self._100um,
                'nas1638': self.nas1638,
                'iso4406_1': self.iso4406_1,
                'iso4406_2': self.iso4406_2,
                'iso4406_3': self.iso4406_3,
                }


class NormIsolation(db.Model):

    __tablename__ = 'norm_isolation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    c = db.Column('c', db.Float(53), server_default=db.text("0"))
    f = db.Column('f', db.Float(53), server_default=db.text("0"))
    notseal = db.Column('notseal', db.Float(53), server_default=db.text("0"))
    seal = db.Column('seal', db.Float(53), server_default=db.text("0"))

    def __repr__(self):
        return "{} {}".format(self.__tablename__, self.id)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'c': self.c,
                'f': self.f,
                'notseal': self.notseal,
                'seal': self.seal,
                }


class NormFuran(db.Model):

    __tablename__ = 'norm_furan'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(50), index=True)
    c1 = db.Column(db.Float(53), server_default=db.text("0"))
    c2 = db.Column(db.Float(53), server_default=db.text("0"))
    c3 = db.Column(db.Float(53), server_default=db.text("0"))
    c4 = db.Column(db.Float(53), server_default=db.text("0"))

    def __repr__(self):
        return self.name

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'c1': self.c1,
                'c2': self.c2,
                'c3': self.c3,
                'c4': self.c4,
                }


class TestSamplingCard(db.Model):

    __tablename__ = 'test_sampling_card'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    test_result_id = db.Column(db.Integer, db.ForeignKey("test_result.id"))
    test_result = db.relationship('TestResult', foreign_keys='TestSamplingCard.test_result_id')
    date_created = db.Column(db.DateTime)
    printed = db.Column(db.Boolean)

    def __repr__(self):
        return "{} created at {}".format(self.id, self.date_created)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'test_result_id': self.test_result_id,
                'date_created': self.date_created,
                'printed': self.printed,
                }


class Country(db.Model):

    __tablename__ = 'country'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.Unicode)
    iso_name = db.Column(db.String(2))

    def __repr__(self):
        return u"{} ({})".format(self.name, self.iso_name)

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'iso_name': self.iso_name,
                }
