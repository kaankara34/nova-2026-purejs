/* Floor plan data for The Residences East West — EAST and WEST buildings.
   Areas transcribed from the architectural drawings. TOTAL AREA is the sum of
   every row listed for that plan, balconies and terraces included. Shared
   circulation (floor lobby, fire escape stair, service stair, lifts, roof void)
   is not part of an apartment and is not listed; the fire lobby (Y.G.H.)
   belongs to the apartment and is included. */
window.EW_PLANS = (function () {
  'use strict';

  var CORE_3PLUS1 = [
    { name: 'Master Bedroom', size: '20.22 m²' },
    { name: 'Master Bathroom', size: '4.60 m²' },
    { name: 'Bedroom', size: '12.05 m²' },
    { name: 'Bedroom', size: '11.84 m²' },
    { name: 'Kitchen', size: '13.29 m²' },
    { name: 'Hall', size: '8.69 m²' },
    { name: 'Bathroom', size: '4.55 m²' },
    { name: 'Guest WC', size: '2.52 m²' },
    { name: 'Entrance Hall', size: '6.84 m²' },
    { name: 'Fire Lobby', size: '3.00 m²' }
  ];

  var CORE_4PLUS1 = [
    { name: 'Master Bedroom', size: '15.81 m²' },
    { name: 'Master Bathroom', size: '3.20 m²' },
    { name: 'Bedroom', size: '9.86 m²' },
    { name: 'Bedroom', size: '9.64 m²' },
    { name: 'Bedroom', size: '9.86 m²' },
    { name: 'Kitchen', size: '13.29 m²' },
    { name: 'Hall', size: '8.69 m²' },
    { name: 'Bathroom', size: '4.55 m²' },
    { name: 'Guest WC', size: '2.52 m²' },
    { name: 'Entrance Hall', size: '6.84 m²' },
    { name: 'Fire Lobby', size: '3.00 m²' }
  ];

  var FRENCH_7 = { name: 'French Balconies (7)', size: '8.46 m²' };
  var FRENCH_4 = { name: 'French Balconies (4)', size: '5.07 m²' };

  function typical(salon, balcony, core, french) {
    return [{ name: 'Living / Dining Room', size: salon }]
      .concat(core)
      .concat([{ name: 'Balcony', size: balcony }, french]);
  }

  function duplexLower(salon, wc, balcony) {
    return [
      { name: 'Living / Dining Room', size: salon },
      { name: 'Master Bedroom', size: '16.75 m²' },
      { name: 'Master Bathroom', size: '4.60 m²' },
      { name: 'Kitchen', size: '18.83 m²' },
      { name: 'Utility Room', size: '4.89 m²' },
      { name: 'Shower Room', size: '2.52 m²' },
      { name: 'Guest WC', size: wc },
      { name: 'Corridor', size: '8.45 m²' },
      { name: 'Entrance Hall', size: '6.66 m²' },
      { name: 'Balcony', size: balcony },
      FRENCH_4
    ];
  }

  function duplexUpper(master) {
    return [
      { name: 'Master Bedroom', size: master },
      { name: 'Master Bathroom', size: '7.92 m²' },
      { name: 'Bedroom', size: '17.90 m²' },
      { name: 'Bathroom', size: '3.02 m²' },
      { name: 'Bedroom', size: '10.00 m²' },
      { name: 'Bathroom', size: '3.06 m²' },
      { name: 'Corridor', size: '4.62 m²' },
      { name: 'Entrance Hall', size: '2.04 m²' },
      { name: 'Terraces (3)', size: '9.52 m²' }
    ];
  }

  var P = 'media/images/ew/plans/';

  return {
    EAST: [
      {
        title: '3+1',
        img: P + 'east-3plus1.webp',
        dim: null,
        total: '142.50 m² / 1,534 sq ft',
        rooms: typical('39.33 m²', '7.11 m²', CORE_3PLUS1, FRENCH_7)
      },
      {
        title: '4+1',
        img: P + 'east-4plus1.webp',
        dim: 'left',
        total: '142.16 m² / 1,530 sq ft',
        rooms: typical('39.33 m²', '7.11 m²', CORE_4PLUS1, FRENCH_7)
      },
      {
        title: 'DUPLEX — LOWER FLOOR',
        img: P + 'east-duplex-lower.webp',
        dim: null,
        total: '136.38 m² / 1,468 sq ft — duplex 224.27 m² / 2,414 sq ft',
        rooms: duplexLower('59.05 m²', '2.56 m²', '7.00 m²')
      },
      {
        title: 'DUPLEX — UPPER FLOOR',
        img: P + 'east-duplex-upper.webp',
        dim: null,
        total: '87.89 m² / 946 sq ft — duplex 224.27 m² / 2,414 sq ft',
        rooms: duplexUpper('29.81 m²')
      }
    ],
    WEST: [
      {
        title: '3+1',
        img: P + 'west-3plus1.webp',
        dim: null,
        total: '138.40 m² / 1,490 sq ft',
        rooms: typical('36.80 m²', '5.54 m²', CORE_3PLUS1, FRENCH_7)
      },
      {
        title: '4+1',
        img: P + 'west-4plus1.webp',
        dim: 'left',
        total: '138.06 m² / 1,486 sq ft',
        rooms: typical('36.80 m²', '5.54 m²', CORE_4PLUS1, FRENCH_7)
      },
      {
        title: 'DUPLEX — LOWER FLOOR',
        img: P + 'west-duplex-lower.webp',
        dim: null,
        total: '132.45 m² / 1,426 sq ft — duplex 217.48 m² / 2,341 sq ft',
        rooms: duplexLower('56.51 m²', '2.73 m²', '5.44 m²')
      },
      {
        title: 'DUPLEX — UPPER FLOOR',
        img: P + 'west-duplex-upper.webp',
        dim: null,
        total: '85.03 m² / 915 sq ft — duplex 217.48 m² / 2,341 sq ft',
        rooms: duplexUpper('26.95 m²')
      }
    ]
  };
})();
