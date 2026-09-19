import { LookupFormController } from '../lookup/lookupFormController.js';


export class LookupBootstrap {
   static start() {
      LookupFormController.bind(
         document.querySelector('#lookup-form'),
         document.querySelector('#projection')
      );
   }


   static {
      document.addEventListener('DOMContentLoaded', () => {
         LookupBootstrap.start();
      });
   }
}
