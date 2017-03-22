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

import React from 'react';
import { translate } from 'react-i18next';
import Logout from 'src/common/logout/logout';
import './header.scss';

export const Header = ({ t }) => (
  <header className='header-wrapper'>
    <div className='header-content'>
      <a href='/'>
        <img
          className='header-logo'
          src='/public/images/logo-orange.svg'
          alt={t('Pixelated')}
        />
      </a>
      <div className='header-icons'>
        <Logout />
      </div>
    </div>
  </header>
);

Header.propTypes = {
  t: React.PropTypes.func.isRequired
};

export default translate('', { wait: true })(Header);
