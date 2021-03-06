import { shallow } from 'enzyme';
import expect from 'expect';
import React from 'react';
import fetchMock from 'fetch-mock';
import { BackupEmail } from 'src/backup_account/backup_email/backup_email';

describe('BackupEmail', () => {
  let backupEmail;
  let mockOnSubmit;
  let mockTranslations;
  let backupEmailInstance;

  beforeEach(() => {
    mockOnSubmit = expect.createSpy();

    mockTranslations = key => key;
    backupEmail = shallow(<BackupEmail t={mockTranslations} onSubmit={mockOnSubmit} />);
  });

  it('renders backup email title', () => {
    expect(backupEmail.find('h1').text()).toEqual('backup-account.backup-email.title');
  });

  it('renders backup account email input field', () => {
    expect(backupEmail.find('InputField').props().name).toEqual('email');
  });

  it('renders backup account submit button', () => {
    expect(backupEmail.find('SubmitButton').props().buttonText).toEqual('backup-account.backup-email.button');
  });

  describe('Email validation', () => {
    beforeEach(() => {
      backupEmailInstance = backupEmail.instance();
    });

    it('verify initial state', () => {
      expect(backupEmailInstance.state.error).toEqual('');
      expect(backupEmail.find('SubmitButton').props().disabled).toBe(true);
    });

    context('with invalid email', () => {
      beforeEach(() => {
        backupEmailInstance.validateEmail({ target: { value: 'test' } });
      });

      it('sets error in state', () => {
        expect(backupEmailInstance.state.error).toEqual('backup-account.backup-email.error.invalid-email');
      });

      it('disables submit button', () => {
        expect(backupEmail.find('SubmitButton').props().disabled).toBe(true);
      });
    });

    context('with valid email', () => {
      beforeEach(() => {
        backupEmailInstance.validateEmail({ target: { value: 'test@test.com' } });
      });

      it('does not set error in state', () => {
        expect(backupEmailInstance.state.error).toEqual('');
      });

      it('submit button is enabled', () => {
        expect(backupEmail.find('SubmitButton').props().disabled).toBe(false);
      });
    });

    context('with empty email', () => {
      beforeEach(() => {
        backupEmailInstance.validateEmail({ target: { value: '' } });
      });

      it('not set error in state', () => {
        expect(backupEmailInstance.state.error).toEqual('');
      });

      it('disables submit button', () => {
        expect(backupEmail.find('SubmitButton').props().disabled).toBe(true);
      });
    });
  });

  describe('Email changing handler', () => {
    beforeEach(() => {
      backupEmailInstance = backupEmail.instance();
    });

    it('sets user backup email in the state', () => {
      backupEmailInstance.handleChange({ target: { value: 'test@test.com' } });
      expect(backupEmailInstance.state.backupEmail).toEqual('test@test.com');
    });
  });

  describe('Submit', () => {
    let preventDefaultSpy;

    beforeEach(() => {
      preventDefaultSpy = expect.createSpy();
    });

    context('on success', () => {
      beforeEach((done) => {
        mockOnSubmit = expect.createSpy().andCall(() => done());

        fetchMock.post('/backup-account', 204);
        backupEmail = shallow(<BackupEmail t={mockTranslations} onSubmit={mockOnSubmit} />);

        backupEmail.find('InputField').simulate('change', { target: { value: 'test@test.com' } });
        backupEmail.find('form').simulate('submit', { preventDefault: preventDefaultSpy });
      });

      it('posts backup email', () => {
        expect(fetchMock.called('/backup-account')).toBe(true, 'Backup account POST was not called');
      });

      it('sends user email as content', () => {
        expect(fetchMock.lastOptions('/backup-account').body).toContain('"backupEmail":"test@test.com"');
      });

      it('calls onSubmit from props with success', () => {
        expect(mockOnSubmit).toHaveBeenCalledWith('success');
      });
    });

    context('on error', () => {
      beforeEach((done) => {
        mockOnSubmit = expect.createSpy().andCall(() => done());

        fetchMock.post('/backup-account', 500);
        backupEmail = shallow(<BackupEmail t={mockTranslations} onSubmit={mockOnSubmit} />);
        backupEmail.find('form').simulate('submit', { preventDefault: preventDefaultSpy });
      });

      it('calls onSubmit from props with error', () => {
        expect(mockOnSubmit).toHaveBeenCalledWith('error');
      });
    });
  });

  afterEach(() => {
    fetchMock.restore();
  });
});
