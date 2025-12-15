from dataclasses import dataclass

@dataclass
class LineItem:
  description: str
  quantity: float
  unit_price: float
  total_price: float

@dataclass
class Digest:
  invoice_number: str
  invoice_date: str
  due_date: str
  total_amount: float
  line_items: list[LineItem]