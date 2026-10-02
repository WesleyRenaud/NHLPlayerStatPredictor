import { PlayerNameBinder } from './playerNameBinder.js';
import { PlayerSearchLabel } from './playerSearchLabel.js';
import { ProjectionClient } from '../api/projectionClient.js';


export class LookupFormController {
   static seasonStats = new WeakMap();
   static playerHistories = new WeakMap();


   static bind(form, result) {
      const input = form.querySelector('#player-name');
      LookupFormController.bindSeasonTabs(result);

      form.addEventListener('submit', async event => {
         event.preventDefault();
         const player = PlayerNameBinder.player(input);

         if (!player) {
            LookupFormController.showError(form);
            return;
         }

         LookupFormController.clearError(form);
         LookupFormController.setBusy(form, true);

         try {
            const projection = await ProjectionClient.get(player.playerId);
            LookupFormController.render(result, player, projection);
         } finally {
            LookupFormController.setBusy(form, false);
         }
      });

      input.addEventListener('input', () => {
         LookupFormController.clearError(form);
      });
   }


   static showError(form) {
      const input = form.querySelector('#player-name');
      const button = form.querySelector('button[type="submit"]');
      form.querySelector('#lookup-error').hidden = false;
      input.classList.add('is-invalid');
      input.setAttribute('aria-invalid', 'true');
      button.classList.remove('is-invalid');
      button.offsetWidth;
      button.classList.add('is-invalid');
   }


   static clearError(form) {
      const input = form.querySelector('#player-name');
      form.querySelector('#lookup-error').hidden = true;
      input.classList.remove('is-invalid');
      input.removeAttribute('aria-invalid');
      form.querySelector('button[type="submit"]').classList.remove('is-invalid');
   }


   static setBusy(form, busy) {
      const button = form.querySelector('button[type="submit"]');
      button.disabled = busy;
      button.classList.toggle('is-busy', busy);
      button.setAttribute('aria-busy', String(busy));
   }


   static render(result, player, projection) {
      LookupFormController.playerHistories.set(result, { playerName: player.playerName, ...projection.playerHistory });
      result.querySelector('[data-player-name]').textContent = player.playerName;
      result.querySelector('[data-player-meta]').textContent =
         PlayerSearchLabel.meta(player);
      LookupFormController.renderStats(
         result.querySelector('[data-projection-stats]'), projection, projection.projectedToi);
      const season = projection.seasonStats;
      LookupFormController.seasonStats.set(result, season);
      result.querySelector('[data-season-stats-container]').hidden = !season;
      if (season) {
         result.querySelector('[data-season-tab="pace"]').disabled = !season.fullSeasonPace;
         LookupFormController.selectSeasonTab(result, 'current');
      }
      result.hidden = false;
      result.classList.remove('is-updated');
      result.offsetWidth;
      result.classList.add('is-updated');
   }


   static bindSeasonTabs(result) {
      for (const mode of ['current', 'pace']) {
         const tab = result.querySelector(`[data-season-tab="${mode}"]`);
         tab.addEventListener('click', () => LookupFormController.selectSeasonTab(result, mode));
         tab.addEventListener('keydown', event => {
            if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
            event.preventDefault();
            const nextMode = event.key === 'Home' ? 'current' : event.key === 'End' ? 'pace' :
               mode === 'current' ? 'pace' : 'current';
            const nextTab = result.querySelector(`[data-season-tab="${nextMode}"]`);
            if (nextTab.disabled) return;
            LookupFormController.selectSeasonTab(result, nextMode);
            nextTab.focus();
         });
      }
   }


   static selectSeasonTab(result, mode) {
      const season = LookupFormController.seasonStats.get(result);
      const stats = mode === 'pace' ? season.fullSeasonPace : season;
      for (const tabMode of ['current', 'pace']) {
         const tab = result.querySelector(`[data-season-tab="${tabMode}"]`);
         tab.setAttribute('aria-selected', String(tabMode === mode));
         tab.tabIndex = tabMode === mode ? 0 : -1;
      }
      const panel = result.querySelector('[data-season-stats]');
      panel.setAttribute('aria-labelledby', mode === 'pace' ? 'full-season-pace-tab' : 'current-statline-tab');
      LookupFormController.renderStats(panel, stats, stats.timeOnIcePerGame);
   }


   static renderStats(result, projection, toi) {
      result.querySelector('[data-goals]').textContent = projection.goals;
      result.querySelector('[data-assists]').textContent = projection.assists;
      result.querySelector('[data-points]').textContent = projection.points;
      LookupFormController.renderOptionalValue(
         result.querySelector('[data-penalty-minutes]'), projection.penaltyMinutes);
      result.querySelector('[data-games-played]').textContent = projection.gamesPlayed;
      LookupFormController.renderOptionalValue(result.querySelector('[data-shots]'), projection.shots);
      LookupFormController.renderOptionalValue(
         result.querySelector('[data-shooting-percentage]'), projection.shootingPercentage?.toFixed(1));
      result.querySelector('[data-even-strength-goals]').textContent = projection.evenStrengthGoals;
      result.querySelector('[data-even-strength-points]').textContent = projection.evenStrengthPoints;
      result.querySelector('[data-power-play-goals]').textContent = projection.powerPlayGoals;
      result.querySelector('[data-power-play-points]').textContent = projection.powerPlayPoints;
      result.querySelector('[data-short-handed-goals]').textContent = projection.shortHandedGoals;
      result.querySelector('[data-short-handed-points]').textContent = projection.shortHandedPoints;
      LookupFormController.renderOptionalValue(result.querySelector('[data-toi]'), toi);
   }


   static renderOptionalValue(element, value) {
      const unavailable = value == null || value === '';
      element.textContent = unavailable ? '—' : value;
      element.classList.toggle('is-unavailable', unavailable);
   }
}
