from app.extensions import ma
from app.models import Skill


class SkillSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Skill


skill_schema = SkillSchema()
skills_schema = SkillSchema(many=True)
