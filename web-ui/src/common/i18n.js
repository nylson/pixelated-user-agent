/*
 * Copyright (c) 2017 ThoughtWorks, Inc.
 *
 * Pixelated is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Pixelated is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
 */
import i18n from 'i18next';
import i18nBackend from 'i18nextXHRBackend';
import I18nDetector from 'i18nextBrowserLanguageDetector';

const detector = new I18nDetector();
const detect = detector.detect.bind(detector);

detector.detect = (detectionOrder) => {
  const result = detect(detectionOrder);
  return result.replace('-', '_');
};

i18n
  .use(i18nBackend)
  .use(detector)
  .init({
    fallbackLng: 'en_US',
    parseMissingKeyHandler: key => (`"${key} untranslated"`),
    backend: {
      loadPath: 'public/locales/{{lng}}/{{ns}}.json'
    }
  });

export default i18n;
