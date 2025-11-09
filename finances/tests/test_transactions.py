# tests/test_transactions.py
class TransactionTests(TestCase):
    def test_create_transaction_updates_budget(self):
        """Verifica que crear gasto actualice presupuesto"""
        
    def test_high_expense_creates_notification(self):
        """Verifica alerta de gasto alto"""
        
    def test_cannot_delete_category_with_transactions(self):
        """Verifica PROTECT en Category"""

# tests/test_goals.py
class FinancialGoalTests(TestCase):
    def test_goal_achieved_when_target_reached(self):
        """Verifica que meta se marca como alcanzada"""
        
    def test_notification_sent_on_goal_completion(self):
        """Verifica notificación al completar meta"""

# tests/test_permissions.py
class PermissionTests(TestCase):
    def test_user_cannot_see_others_transactions(self):
        """Verifica aislamiento de datos por usuario"""