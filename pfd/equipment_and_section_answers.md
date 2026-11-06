# Major equipment estimates and Reactor / Separator section answers

Basis: your mass balance (100,000 t/y methanol, 8,000 h/y, 99.9 wt% methanol, X = 18 % per pass, H2:CO2 = 3.2 at the reactor, 0.5 % purge, no side reactions).
Everything marked *estimate* comes from my own calculation (ideal-gas heat capacities and a shortcut column model) and must be confirmed by a simulation.

## 1. Important correction to the reactor temperature

With this mass balance, stream 3 contains only CO2 and H2 (no diluent), and the reaction heat at reactor temperature is about -57 kJ/mol (the -49 kJ/mol figure is for 25 C).

| Reactor inlet | Adiabatic outlet (estimate) | Equilibrium CO2 conversion at the outlet temperature |
|---|---|---|
| 210 C | about 287 C | about 15.8 % (below your 18 %) |
| 230 C | about 308 C | below 15 % |

An uncooled reactor therefore cannot give 18 % per pass and would run far above the 260 C limit of the lecture. My earlier "+40 K, outlet about 250 C" assumed recycle dilution that your mass balance does not have. A cooled reactor (boiling water on the shell side) is needed. Equilibrium CO2 conversion at 50 bar, H2:CO2 = 3.2 (methanol reaction only, ideal gas): 26.4 % at 230 C, 22.1 % at 250 C, so 18 % is 68-81 % of equilibrium.

## 2. Major equipment (estimates)

| Equipment | Key data |
|---|---|
| R-101 | Fixed-bed multitubular, cooled by boiling water; Cu/ZnO/Al2O3; 50 bar, 230 C; feed 9,114.6 kmol/h (109.4 t/h), about 7,300 m3/h at 210 C, 50 bar; heat removed about 6.2 MW (about 12 t/h steam); catalyst volume about 20-41 m3 if GHSV is 5,000-10,000 1/h (assumed GHSV, replace with kinetics) |
| V-101 | Vertical flash drum, 49 bar, 45 C; gas 1.13 m3/s (89.8 t/h), liquid 22 m3/h (19.5 t/h); diameter about 1.8 m (Souders-Brown K = 0.07 m/s assumed) |
| T-101 | 1.2 bar, top 68.9 C, bottom 104.6 C; feed 781 kmol/h (19.5 t/h), 1:1 CH3OH:H2O; distillate 390.9 kmol/h, bottoms 390.3 kmol/h; Rmin 0.76, R = 1.3 Rmin = 0.99; about 30 theoretical stages (feed stage about 24 from the top), about 43 trays at an assumed 70 % efficiency; condenser about 7.6 MW, reboiler about 7.8 MW |
| K-101 (CO2, 1 -> 50 bar) | 4 stages, about 1.7 MW |
| K-102 (H2) | 30 -> 50 bar, 1 stage: about 0.6 MW; from 1 bar, 4 stages: about 5.2 MW |
| K-103 (recycle, 7,514 kmol/h) | 49 -> 50 bar, about 0.15 MW |
| E-101 | 45 -> 210 C: about 13.4 MW (15.0 MW to 230 C) |
| E-102 | cool 250 C -> 45 C with condensation: about 24.5 MW (about 590 kg/s cooling water) |
| E-103 | 45 -> 70 C: about 0.4 MW |
| E-104 / E-105 | about 7.6 MW / 7.8 MW |
| P-102 | distillate + reflux = (R+1) x D = about 25 t/h |
| P-103 | about 7.0 t/h water |

E-102 (24.5 MW) releases more heat than E-101 needs (13.4 MW): a feed-effluent exchanger is worth showing (Table 6.4: heat integration).

## 3. Reactor section questions

1. **Phase:** gas phase over a solid catalyst (gas-solid). Methanol and water are only about 4.7 mol % each, so they stay as vapour at 230 C.
2. **T and P ranges:** literature 200-300 C; experiments on Cu/ZnO/Al2O3 at 200-230 C and 50-80 bar. Chosen: 230 C, 50 bar. 50 bar is above the 10 bar lecture limit and is justified by the 4 -> 2 mole reduction (Table 6.2).
3. **Kinetic or equilibrium controlled:** equilibrium sets the ceiling (26 % at 230 C, 50 bar), kinetics decides how close you get (18 % is 68 % of it). The low per-pass value is why the recycle is needed.
4. **Solid catalyst or homogeneous:** solid, heterogeneous Cu/ZnO/Al2O3.
5. **Exothermic or endothermic:** exothermic: -49 kJ/mol at 25 C, about -57 kJ/mol at 210-230 C; about 6.2 MW at your flow. Cooling is needed.
6. **Side reactions and selectivity:** your mass balance assumes none (100 % selectivity, assumption 5). In reality the reverse water-gas shift (CO2 + H2 -> CO + H2O, endothermic) becomes more favoured as temperature rises, so selectivity falls with T and CO appears in the recycle. State this as a simplification.
7. **Single-pass conversion:** 18 % of CO2 (your assumption; Kiss et al. 17.2 % CO2 per pass, quoted in your document; JRC about 21 %).

## 4. Separator section questions

1. **Units:** V-101 vapour-liquid flash drum (CO2/H2 out as gas), then T-101 distillation column for the methanol-water liquid (the NRTL equilibrium curve shows no azeotrope). The purge is a simple splitter.
2. **Sequence:** reactor -> E-102 cool and condense -> V-101 flash -> E-103 pre-heat -> T-101. Gases are removed first because their volatility differs hugely from the liquids; distillation then uses the volatility difference between methanol and water.
3. **Product specs:** stream 9 (methanol): 99.9 wt% CH3OH, 0.1 wt% H2O, 12.5 t/h, 99.9 % recovery. Stream 8 (water): about 99.8 wt% water with 0.18 wt% methanol, 7.03 t/h. Stream 10 (purge): 37.8 kmol/h, 23.6 mol % CO2 and 76.4 mol % H2 (0.45 t/h). No discharge or vent limits are given in your document.
4. **Heat-sensitive products:** none in the separation section. Methanol and water are stable at 69-105 C. The temperature-sensitive item is the catalyst in R-101.
5. **Hazards:** methanol is toxic and flammable; H2 is flammable and explosive and attacks steel at 50 bar; CO2 is an asphyxiant; the purge (H2/CO2) must go to a flare or safe vent; the water carries 0.18 wt% methanol and needs treatment. (General safety knowledge, not from a source I read.)

## 5. Inconsistencies between your mass balance and the PFD file

- Your mass balance numbers the streams: 8 = water (bottoms), 9 = methanol (distillate), 10 = purge. The PFD file has 8 = overhead and 9 = bottoms and no stream 10.
- Equipment names differ (C-101 in the document, K-101 in the file).
- Stream 3 and the recycle contain no CO in your mass balance; the PFD stream table lists CO.
