from gaelib.db import model, properties

class SampleModel(model.Model):
    """
        Test database
    """
    string1 = properties.StringProperty()
    string2 = properties.StringProperty()
    int1 = properties.IntegerProperty()
    float1 = properties.FloatProperty()
    bool1 = properties.BooleanProperty()
