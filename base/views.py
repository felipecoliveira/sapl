import os
from functools import lru_cache

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin
from vanilla import GenericView

import sapl

from .models import CasaLegislativa


@lru_cache(maxsize=1)
def get_casalegislativa():
    return CasaLegislativa.objects.first()


class HelpView(TemplateView):
    # XXX treat non existing template as a 404!!!!

    def get_template_names(self):
        return ['ajuda/%s.html' % self.kwargs['topic']]


ESTADOS = {"": "",
           "AC": "ACRE",
           "AL": "ALAGOAS",
           "AM": "AMAZONAS",
           "AP": "AMAPÁ",
           "BA": "BAHIA",
           "CE": "CEARÁ",
           "DF": "DISTRITO FEDERAL",
           "ES": "ESPíRITO SANTO",
           "GO": "GOIÁS",
           "MA": "MARANHÃO",
           "MG": "MINAS GERAIS",
           "MS": "MATO GROSSO DO SUL",
           "MT": "MATO GROSSO",
           "PA": "PARÁ",
           "PB": "PARAÍBA",
           "PE": "PERNAMBUCO",
           "PI": "PIAUÍ",
           "PR": "PARANÁ",
           "RJ": "RIO DE JANEIRO",
           "RN": "RIO GRANDE DO NORTE",
           "RO": "RONDÔNIA",
           "RR": "RORAIMA",
           "RS": "RIO GRANDE DO SUL",
           "SC": "SANTA CATARINA",
           "SE": "SERGIPE",
           "SP": "SÃO PAULO",
           "TO": "TOCANTINS"}


class CasaLegislativaTabelaAuxForm(ModelForm):

    uf = forms.ChoiceField(required=True,
                           label='UF',
                           choices=[(uf, uf) for uf in ESTADOS.keys()],
                           widget=forms.Select(
                               attrs={'class': 'selector'}))

    informacao_geral = forms.CharField(widget=forms.Textarea,
                                       label='Informação Geral',
                                       required=False)

    telefone = forms.CharField(label='Telefone',
                               required=False,
                               widget=forms.TextInput(
                                   attrs={'class': 'telefone'}))

    logotipo = forms.ImageField(label='Logotipo',
                                required=False,
                                widget=forms.FileInput
                                )

    cep = forms.CharField(label='Cep',
                          required=True,
                          widget=forms.TextInput(
                              attrs={'class': 'cep'}))

    fax = forms.CharField(label='Fax',
                          required=False,
                          widget=forms.TextInput(
                              attrs={'class': 'telefone'}))

    class Meta:

        model = CasaLegislativa
        fields = ['codigo',
                  'nome',
                  'sigla',
                  'endereco',
                  'cep',
                  'municipio',
                  'uf',
                  'telefone',
                  'fax',
                  'logotipo',
                  'endereco_web',
                  'email',
                  'informacao_geral']

    def __init__(self, *args, **kwargs):

        row1 = sapl.layout.to_row(
            [('codigo', 2),
             ('nome', 5),
             ('sigla', 5)])

        row2 = sapl.layout.to_row(
            [('endereco', 8),
             ('cep', 4)])

        row3 = sapl.layout.to_row(
            [('municipio', 10),
             ('uf', 2)])

        row4 = sapl.layout.to_row(
            [('telefone', 6),
             ('fax', 6)])

        row5 = sapl.layout.to_row(
            [('logotipo', 12)])

        row6 = sapl.layout.to_row(
            [('endereco_web', 12)])

        row7 = sapl.layout.to_row(
            [('email', 12)])

        row8 = sapl.layout.to_row(
            [('informacao_geral', 12)])

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Dados Básicos',
                row1,
                row2,
                row3,
                row4,
                row5,
                HTML("""{% if form.logotipo.value %}
                        <img class="img-responsive" width="225" height="300"
                             src="{{ MEDIA_URL }}{{ form.logotipo.value }}">
                             <br /><br />
                        <input type="submit"
                               name="remover"
                               id="remover"
                               class="button primary"
                               value="Remover Logo"/>
                         {% endif %}""", ),
                row6,
                row7,
                row8,
                ButtonHolder(
                    Submit('submit', 'Salvar',
                           css_class='button primary')
                )
            )
        )
        super(CasaLegislativaTabelaAuxForm, self).__init__(*args, **kwargs)


class CasaLegislativaTableAuxView(FormMixin, GenericView):

    template_name = "base/casa_leg_table_aux.html"

    def get(self, request, *args, **kwargs):
        try:
            casa = CasaLegislativa.objects.first()
        except ObjectDoesNotExist:
            form = CasaLegislativaTabelaAuxForm()
        else:
            form = CasaLegislativaTabelaAuxForm(instance=casa)

        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        form = CasaLegislativaTabelaAuxForm(request.POST, request.FILES)

        if form.is_valid():
            casa = CasaLegislativa.objects.first()
            if casa:
                if ("remover" in request.POST or
                   (form.cleaned_data['logotipo'] and casa.logotipo)):
                    try:
                        os.unlink(casa.logotipo.path)
                    except OSError:
                        pass  # Should log this error!!!!!
                    casa.logotipo = None
                casa_save = CasaLegislativaTabelaAuxForm(
                    request.POST,
                    request.FILES,
                    instance=casa
                ).save(commit=False)
                casa_save.save()
            else:
                form.save()

            # Invalida cache de consulta
            get_casalegislativa.cache_clear()

            return self.form_valid(form)
        else:
            return self.render_to_response({'form': form})

    def get_success_url(self):
        return reverse('casa_legislativa')
