'''
This file is part of Vyolet.

    Vyolet is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Vyolet is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Vyolet.  If not, see <http://www.gnu.org/licenses/>.
'''

SHORTS = ('A', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na',
          'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V',
          'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se',
          'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh',
          'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba',
          'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho',
          'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt',
          'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac',
          'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
          'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg',
          'Cn', 'Uut', 'Fl', 'Uup', 'Lv', 'Uus', 'Uuo')

LONGS = ('Atom', 'Hydrogen', 'Helium', 'Lithium', 'Beryllium', 'Boron',
         'Carbon', 'Nitrogen', 'Oxygen', 'Fluorine', 'Neon', 'Sodium',
         'Magnesium', 'Aluminium', 'Silicon', 'Phosphorus', 'Sulfur',
         'Chlorine', 'Argon', 'Potassium', 'Calcium', 'Scandium', 'Titanium',
         'Vanadium', 'Chromium', 'Manganese', 'Iron', 'Cobalt', 'Nickel',
         'Copper', 'Zinc', 'Gallium', 'Germanium', 'Arsenic', 'Selenium',
         'Bromine', 'Krypton', 'Rubidium', 'Strontium', 'Yttrium',
         'Zirconium', 'Niobium', 'Molybdenum', 'Technetium', 'Ruthenium',
         'Rhodium', 'Palladium', 'Silver', 'Cadmium', 'Indium', 'Tin',
         'Antimony', 'Tellurium', 'Iodine', 'Xenon', 'Caesium', 'Barium',
         'Lanthanum', 'Cerium', 'Praseodymium', 'Neodymium', 'Promethium',
         'Samarium', 'Europium', 'Gadolinium', 'Terbium', 'Dysprosium',
         'Holmium', 'Erbium', 'Thulium', 'Ytterbium', 'Lutetium', 'Hafnium',
         'Tantalum', 'Tungsten', 'Rhenium', 'Osmium', 'Iridium', 'Platinum',
         'Gold', 'Mercury', 'Thallium', 'Lead', 'Bismuth', 'Polonium',
         'Astatine', 'Radon', 'Francium', 'Radium', 'Actinium', 'Thorium',
         'Protactinium', 'Uranium', 'Neptunium', 'Plutonium', 'Americium',
         'Curium', 'Berkelium', 'Californium', 'Einsteinium', 'Fermium',
         'Mendelevium', 'Nobelium', 'Lawrencium', 'Rutherfordium', 'Dubnium',
         'Seaborgium', 'Bohrium', 'Hassium', 'Meitnerium', 'Darmstadtium',
         'Roentgenium', 'Copernicium', 'Ununtrium', 'Flerovium',
         'Ununpentium', 'Livermorium', 'Ununseptium', 'Ununoctium')


class Version(object):
    def __init__(self, vtup):
        self.tuple_ = vtup
        self.long = self._makelong(vtup)
        self.short = self._makeshort(vtup)

    def _makelong(self, vtup):
        if len(vtup) == 2:
            return '-'.join((LONGS[vtup[0]], str(vtup[1])))
        else:
            return '{}-{} ({})'.format(
                    LONGS[vtup[0]], vtup[1], vtup[2])

    def _makeshort(self, vtup):
        if len(vtup) == 2:
            return '-'.join((SHORTS[vtup[0]], str(vtup[1])))
        else:
            return '{}-{}{}'.format(
                    SHORTS[vtup[0]], vtup[1], vtup[2][0])

    def __repr__(self):
        return 'Version(%r)' % (self.tuple_,)
