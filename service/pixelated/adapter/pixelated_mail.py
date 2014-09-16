#
# Copyright (c) 2014 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
from pixelated.adapter.status import Status
from pixelated.support.id_gen import gen_pixelated_uid
import json
import pixelated.support.date
import dateutil.parser as dateparser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


class PixelatedMail:

    def __init__(self):
        self.body = ''
        self.headers = {}
        self.status = []
        self.security_casing = {}
        self.tags = []

    @staticmethod
    def from_leap_mail(leap_mail, leap_mailbox=None):
        mail = PixelatedMail()
        mail.leap_mail = leap_mail
        mail.leap_mailbox = leap_mailbox
        mail.body = leap_mail.bdoc.content['raw']
        mail.headers = mail._extract_headers()
        mail.headers['date'] = PixelatedMail._get_date(mail.headers)
        mail.status = set(mail._extract_status())
        mail.security_casing = {}
        mail.tags = mail._extract_tags()
        return mail

    @property
    def is_recent(self):
        return Status('recent') in self.status

    @property
    def ident(self):
        return gen_pixelated_uid(self.leap_mailbox.mbox, self.leap_mail.getUID())

    def set_from(self, _from):
        self.headers['from'] = [_from]

    def get_to(self):
        return self.headers['to']

    def get_cc(self):
        return self.headers['cc']

    def get_bcc(self):
        return self.headers['bcc']

    def _extract_status(self):
        return Status.from_flags(self.leap_mail.getFlags())

    def _split_recipients(self, header_type, temporary_headers):
        if(temporary_headers.get(header_type) is not None):
            recipients = temporary_headers[header_type].split(',')
            temporary_headers[header_type] = map(lambda x: x.lstrip(), recipients)

    def _extract_headers(self):
        temporary_headers = {}
        for header, value in self.leap_mail.hdoc.content['headers'].items():
            temporary_headers[header.lower()] = value

        map(lambda x: self._split_recipients(x, temporary_headers), ['to', 'bcc', 'cc'])

        return temporary_headers

    def _extract_tags(self):
        tags = self.headers.get('x-tags', '[]')
        if type(tags) is list:
            return set(tags)
        return set(json.loads(tags))

    def update_tags(self, tags):
        old_tags = self.tags
        self.tags = tags
        removed = old_tags.difference(tags)
        added = tags.difference(old_tags)
        self._persist_mail_tags(tags)
        return added, removed

    def mark_as_read(self):
        self.leap_mail.setFlags((Status.PixelatedStatus.SEEN,), 1)
        self.status = self._extract_status()
        return self

    def mark_as_not_recent(self):
        self.leap_mail.setFlags((Status.PixelatedStatus.RECENT,), -1)
        self.status = self._extract_status()
        return self

    def _persist_mail_tags(self, current_tags):
        hdoc = self.leap_mail.hdoc
        hdoc.content['headers']['X-Tags'] = json.dumps(list(current_tags))
        self.leap_mail._soledad.put_doc(hdoc)

    def has_tag(self, tag):
        return tag in self.tags

    def move_to(self, destiny_mailbox):
        new_leap_mail = destiny_mailbox.add_mail(self)
        self._delete_from_leap_mailbox()
        old_mailbox_tag = self.leap_mailbox.mbox.lower()
        self._update_leap_references(destiny_mailbox.leap_mailbox, new_leap_mail)

        return destiny_mailbox.mailbox_tag, old_mailbox_tag

    def _delete_from_leap_mailbox(self):
        self.leap_mail.setFlags((Status.PixelatedStatus.DELETED,), 1)
        self.leap_mailbox.expunge()

    def _update_leap_references(self, new_leap_mailbox, new_leap_mail):
        self.leap_mailbox = new_leap_mailbox
        self.leap_mail = new_leap_mail

    def raw_message(self):
        raw_message = ''.join("%s: %s\n" % (key, value) for key, value in self.leap_mail.hdoc.content['headers'].items())
        raw_message += '\n\n'
        raw_message += self.leap_mail.bdoc.content['raw']
        return raw_message

    def as_dict(self):
        statuses = [status.name for status in self.status]
        return {
            'header': self.headers,
            'ident': self.ident,
            'tags': list(self.tags),
            'status': statuses,
            'security_casing': self.security_casing,
            'body': self.body
        }

    def to_mime_multipart(self):
        mime_multipart = MIMEMultipart()
        mime_multipart['To'] = ", ".join(self.headers['to'])
        mime_multipart['Cc'] = ", ".join(self.headers['cc'])
        mime_multipart['Bcc'] = ", ".join(self.headers['bcc'])
        mime_multipart['Subject'] = self.headers['subject']
        mime_multipart['Date'] = self.headers['date']
        mime_multipart.attach(MIMEText(self.body, 'plain'))
        return mime_multipart

    def to_smtp_format(self):
        mime_multipart = self.to_mime_multipart()
        mime_multipart['From'] = PixelatedMail.from_email_address
        return mime_multipart.as_string()

    def set_ident(self, mailbox_name, uid):
        self.ident = gen_pixelated_uid(mailbox_name, uid)

    @staticmethod
    def from_dict(mail_dict):
        return from_dict(mail_dict)

    @classmethod
    def _get_date(cls, headers):
        date = headers.get('date', None)
        if not date:
            date = headers['received'].split(";")[-1].strip()
        return dateparser.parse(date).isoformat()


def from_dict(mail_dict):
    mail = PixelatedMail()
    mail.headers = mail_dict.get('header', {})
    mail.headers['date'] = pixelated.support.date.iso_now()
    mail.body = mail_dict.get('body', '')
    mail.ident = mail_dict.get('ident', None)
    mail.tags = set(mail_dict.get('tags', []))
    mail.status = set(mail_dict.get('status', []))
    return mail
