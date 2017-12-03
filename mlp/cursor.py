from collections import OrderedDict


class GeometrySelectCursor:

    def __init__(self, action, available_cells, shape):
        self.action = action
        self.available_cells = available_cells
        if isinstance(shape, list):
            self.shape = OrderedDict()
            for shape_part in shape:
                self.shape[shape_part['name']] = shape_part['area']
        else:
            self.shape = shape
        self._context = {}

    @property
    def context(self):
        context = self.action.context.copy()
        context.update(self._context)
        return context

    def search_in_aoe(self, target):
        for cell in self.available_cells.get(self.context):
            self._context['selected'] = cell
            cells = self.shape.get(self.context)
            if target.cell in cells:
                return cell
