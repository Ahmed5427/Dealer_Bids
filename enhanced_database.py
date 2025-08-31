#!/usr/bin/env python3
"""
Enhanced Database Manager with profile picture column support
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from database import DatabaseManager

logger = logging.getLogger(__name__)

class EnhancedDatabaseManager(DatabaseManager):
    """Enhanced Database Manager with profile picture and status columns"""
    
    def setup_headers(self, worksheet, sheet_name):
        """Enhanced headers with new profile picture columns"""
        headers = {
            "fb_accounts": [
                "account_id", "email", "password", "phone", "proxy_ip", 
                "status", "created_date", "last_active", "messages_sent_today", 
                "marketplace_unlocked", "warmup_phase", "ban_count", 
                "registration_method", "primary_identifier", 
                "profile_picture", "profile_status"  # NEW COLUMNS O and P
            ],
            "leads": [
                "lead_id", "title", "price", "year", "make", "model", 
                "seller_url", "seller_name", "post_date", "scraped_date", 
                "city", "status", "vin", "phone_number", "description"
            ],
            "messages": [
                "message_id", "lead_id", "account_id", "message_text", 
                "sent_at", "reply_received", "reply_text", "phone_extracted", 
                "vin_extracted", "status", "escalated"
            ],
            "account_activity": [
                "activity_id", "account_id", "action_type", "timestamp", 
                "success", "notes", "error_message"
            ]
        }
        
        if sheet_name in headers:
            worksheet.append_row(headers[sheet_name])
    
    def add_enhanced_fb_account(self, email, password, phone, proxy_ip, 
                               registration_method="phone_first", profile_picture="", profile_status="no"):
        """Enhanced method with profile picture support"""
        try:
            worksheet = self.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            account_id = len(records) + 1
            
            # Determine primary identifier
            primary_identifier = phone if registration_method == "phone_first" else email
            
            row = [
                account_id, email, password, phone, proxy_ip,
                "created", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "", 0, "No", "phase_1", 0, 
                registration_method, primary_identifier,
                profile_picture, profile_status  # NEW COLUMNS
            ]
            
            worksheet.append_row(row)
            logger.info(f"Added enhanced FB account: {primary_identifier} (method: {registration_method})")
            return account_id
        except Exception as e:
            logger.error(f"Error adding enhanced FB account: {e}")
            return None
    
    def get_account_profile_status(self, account_id):
        """Get profile picture status for an account"""
        try:
            worksheet = self.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            
            for record in records:
                if str(record['account_id']) == str(account_id):
                    return {
                        'profile_picture': record.get('profile_picture', ''),
                        'profile_status': record.get('profile_status', 'no')
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error getting profile status: {e}")
            return None
    
    def update_profile_picture(self, account_id, profile_picture_path, profile_status="no"):
        """Update profile picture path and status"""
        try:
            worksheet = self.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):
                if str(record['account_id']) == str(account_id):
                    # Update column O (profile_picture) and P (profile_status)
                    worksheet.update_cell(i, 15, profile_picture_path)  # Column O
                    worksheet.update_cell(i, 16, profile_status)        # Column P
                    logger.info(f"Updated profile picture for account {account_id}")
                    return True
            
            logger.error(f"Account {account_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error updating profile picture: {e}")
            return False
    
    def mark_profile_picture_uploaded(self, account_id):
        """Mark profile picture as uploaded (set status to 'yes')"""
        try:
            worksheet = self.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):
                if str(record['account_id']) == str(account_id):
                    worksheet.update_cell(i, 16, 'yes')  # Column P
                    logger.info(f"Marked profile picture as uploaded for account {account_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking profile picture as uploaded: {e}")
            return False
    
    def get_accounts_needing_profile_pictures(self):
        """Get accounts that need profile picture generation or upload"""
        try:
            worksheet = self.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            
            needs_generation = []
            needs_upload = []
            
            for record in records:
                if record.get('status') in ['created', 'warming']:
                    profile_status = record.get('profile_status', 'no')
                    profile_picture = record.get('profile_picture', '')
                    
                    if profile_status != 'yes':
                        if not profile_picture or profile_picture.strip() == '':
                            needs_generation.append(record)
                        else:
                            needs_upload.append(record)
            
            logger.info(f"Found {len(needs_generation)} accounts needing generation, {len(needs_upload)} needing upload")
            return {
                'needs_generation': needs_generation,
                'needs_upload': needs_upload
            }
            
        except Exception as e:
            logger.error(f"Error getting accounts needing profile pictures: {e}")
            return {'needs_generation': [], 'needs_upload': []}
    
    def get_enhanced_active_accounts(self):
        """Get active accounts with profile picture info"""
        try:
            worksheet = self.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            
            active_accounts = []
            for record in records:
                if record['status'] in ['active', 'warming', 'created']:
                    # Ensure profile picture columns exist
                    if 'profile_picture' not in record:
                        record['profile_picture'] = ''
                    if 'profile_status' not in record:
                        record['profile_status'] = 'no'
                    
                    active_accounts.append(record)
            
            return active_accounts
        except Exception as e:
            logger.error(f"Error getting enhanced active accounts: {e}")
            return []
    
    def ensure_profile_columns_exist(self):
        """Ensure profile picture columns exist in the spreadsheet"""
        try:
            worksheet = self.get_worksheet("fb_accounts")
            headers = worksheet.row_values(1)
            
            columns_needed = []
            
            # Check for column O (profile_picture)
            if len(headers) < 15 or headers[14] != 'profile_picture':
                columns_needed.append(('profile_picture', 15))
            
            # Check for column P (profile_status)  
            if len(headers) < 16 or headers[15] != 'profile_status':
                columns_needed.append(('profile_status', 16))
            
            # Add missing columns
            for col_name, col_index in columns_needed:
                worksheet.update_cell(1, col_index, col_name)
                logger.info(f"Added column {col_name} at position {col_index}")
                
                # Initialize existing rows with default values
                records = worksheet.get_all_records()
                for i in range(2, len(records) + 2):
                    if col_name == 'profile_status':
                        worksheet.update_cell(i, col_index, 'no')
                    elif col_name == 'profile_picture':
                        worksheet.update_cell(i, col_index, '')
            
            if columns_needed:
                logger.info(f"Added {len(columns_needed)} missing profile picture columns")
            else:
                logger.info("Profile picture columns already exist")
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring profile columns exist: {e}")
            return False