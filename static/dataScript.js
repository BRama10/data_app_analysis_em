var index = [];
for(let x = 0; x < 18; x++) {
    index.push(x);
}

$(document).ready(() => {
    new ConditionalField({
        control: '.choosetable',
        visibility: {
          'contact': '.humancheck_contact',
          'data': '.humancheck_data'
        }
      });

      new ConditionalField({
        control: '.humancheck_contact',
        visibility: {
          'on': '.'+'conditional',
        }
      });

      new ConditionalField({
        control: '.humancheck_data',
        visibility: {
          'on': '.'+'conditional',
        }
      });

  

    
    for(let x = 0; x< 4; x++) {
        val = '' + x;
        new ConditionalField({
            control: '.contact_' + val,
            visibility: {
              'on': '.value_contact_' + val,
            }
          });
    }

 
    for(let x = 0; x< 15; x++) {
        val = '' + x;
        new ConditionalField({
            control: '.data_' + val,
            visibility: {
              'on': '.value_data_' + val,
            }
          });
    }

    for(let x = 0; x< 4; x++) {
        val = '' + x;
        new ConditionalField({
            control: '.contact_' + val,
            visibility: {
              'on': '.contact_andor_' + val,
            }
          });
    }

    for(let x = 0; x< 15; x++) {
        val = '' + x;
        new ConditionalField({
            control: '.data_' + val,
            visibility: {
              'on': '.data_all_' + val,
            }
          });
    }

    for(let x = 1; x< 3; x++) {
        val = '' + x;
        new ConditionalField({
            control: '.bound_decider_button_' + val,
            visibility: {
              'single': '.num_range_single_' + val,
              'double': '.num_range_double_' + val
            }
          });
    }
      

});

// 4 & 14 respectively