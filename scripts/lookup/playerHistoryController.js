export class PlayerHistoryController {
   static sortStates = new WeakMap();


   static statColumns = [
      'gamesPlayed', 'goals', 'assists', 'points', 'penaltyMinutes',
      'evenStrengthGoals', 'evenStrengthPoints', 'powerPlayGoals', 'powerPlayPoints',
      'shortHandedGoals', 'shortHandedPoints', 'timeOnIcePerGame', 'shots', 'shootingPercentage',
   ];


   static bind(trigger, dialog, historyProvider) {
      for (const button of dialog.querySelectorAll('[data-history-sort]')) {
         button.addEventListener('click', () => PlayerHistoryController.sort(dialog, button.dataset.historySort));
      }
      trigger.addEventListener('click', () => {
         PlayerHistoryController.render(dialog, historyProvider());
         dialog.showModal();
      });
      dialog.addEventListener('click', event => {
         if (event.target !== dialog) return;
         const bounds = dialog.getBoundingClientRect();
         if (event.clientX < bounds.left || event.clientX > bounds.right ||
             event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
      });
   }


   static render(dialog, history) {
      PlayerHistoryController.sortStates.set(dialog, { history, key: null, direction: null });
      PlayerHistoryController.updateSortHeaders(dialog, null, null);
      dialog.querySelector('#history-player-name').textContent = history.playerName;
      PlayerHistoryController.renderSeasons(dialog, history.seasons);
      const career = dialog.querySelector('[data-history-career]');
      while (career.children.length > 1) career.lastElementChild.remove();
      career.hidden = history.career == null;
      if (history.career) PlayerHistoryController.appendStats(career, history.career);
   }


   static renderSeasons(dialog, seasons) {
      const body = dialog.querySelector('[data-history-seasons]');
      body.replaceChildren();
      for (const season of seasons) {
         const row = dialog.ownerDocument.createElement('tr');
         for (const key of ['seasonLabel', 'league', 'team']) {
            const cell = dialog.ownerDocument.createElement(key === 'seasonLabel' ? 'th' : 'td');
            if (key === 'seasonLabel') cell.scope = 'row';
            cell.textContent = season[key];
            row.append(cell);
         }
         PlayerHistoryController.appendStats(row, season);
         body.append(row);
      }
   }


   static sort(dialog, key) {
      const state = PlayerHistoryController.sortStates.get(dialog);
      const direction = state.key === key && state.direction === 'descending' ? 'ascending' : 'descending';
      const seasons = [...state.history.seasons].sort((first, second) => {
         const a = PlayerHistoryController.sortValue(first, key);
         const b = PlayerHistoryController.sortValue(second, key);
         if (a == null && b == null) return 0;
         if (a == null) return 1;
         if (b == null) return -1;
         return direction === 'descending' ? b - a : a - b;
      });
      state.key = key;
      state.direction = direction;
      PlayerHistoryController.renderSeasons(dialog, seasons);
      PlayerHistoryController.updateSortHeaders(dialog, key, direction);
   }


   static sortValue(season, key) {
      const value = season[key];
      if (value == null || key !== 'timeOnIcePerGame') return value;
      const [minutes, seconds] = value.split(':').map(Number);
      return minutes * 60 + seconds;
   }


   static updateSortHeaders(dialog, key, direction) {
      for (const button of dialog.querySelectorAll('[data-history-sort]')) {
         button.parentElement.setAttribute('aria-sort', button.dataset.historySort === key ? direction : 'none');
      }
   }


   static appendStats(row, stats) {
      for (const key of PlayerHistoryController.statColumns) {
         const cell = row.ownerDocument.createElement('td');
         const value = stats[key];
         cell.textContent = value == null ? '—' : key === 'shootingPercentage' ? value.toFixed(1) : value;
         cell.classList.toggle('is-unavailable', value == null);
         row.append(cell);
      }
   }
}
