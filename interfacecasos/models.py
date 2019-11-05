from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

def count():
    last_feature = Feature.objects.all().last()
    last_num = last_feature.num_feature
    if not last_num:
        return 1
    else:
        return int(last_num) + 1 

def countNotification():
    last_feature = Notification.objects.all().last()
    last_num = last_feature.num_feature
    if not last_num:
        return 1
    else:
        return int(last_num) + 1 


class Cargo(models.Model):
    nome_cargo = models.CharField(
        "Nome do cargo",
        max_length=200
    )
    
    def __str__(self):
        return self.nome_cargo

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE
    )
    nome = models.CharField(
        "Nome", 
        max_length = 128
    )
    cargo_usuario = models.ForeignKey(
        Cargo, 
        on_delete=models.CASCADE, 
        blank=False
    )
    data_de_nascimento = models.DateField(
        'Data de nascimento', 
        null=True
    )
    telefone_celular = models.CharField(
        "Telefone celular", 
        max_length=15,
        blank=False,unique=True
    )
    email = models.EmailField(
        'E-mail',
        blank=False,
        unique=True
    )
 
    def __str__(self):
        return "Usuário: " + self.user.username
    
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

class Feature(models.Model):
    name = models.CharField(
        verbose_name="Nome",
        max_length=50,   
    )
    num_feature = models.CharField(
        verbose_name='Número da funcionalidade',
        max_length = 20,
        default=count,
        editable=False
    )
    date_to_finish = models.DateTimeField(
        verbose_name="Data para finalizar"
    )
    author = models.ForeignKey(
        Profile,
        on_delete=models.DO_NOTHING,
        blank = True, 
        null = True
    )
    colaborator = models.ManyToManyField(
        Profile,
        blank = True,
        related_name = 'colaborator'
    )
    date = models.DateTimeField(
        verbose_name="Data de Criação",
        default = timezone.localtime(timezone.now())
    )
    is_finished = models.BooleanField(
        'Finalizado', 
        default=False
    )
    date_finished = models.DateTimeField(
        verbose_name="Data de conclusão",
        blank=True,
        null=True
    )
    min_cases = models.CharField(
        max_length=20,
        verbose_name='Quantidade mínima de casos',
        blank = True,
        null=True,
        editable=False
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Funcionalidade"
        verbose_name_plural="Funcionalidades"

class Precondition(models.Model):
    condittion = models.CharField(
        "Pré-Condição",
        max_length=120
    )

    def __str__(self):
        return self.condittion

    class Meta:
        verbose_name = "Pré-Condição"
        verbose_name_plural = "Pré-Condições"

class Expected(models.Model):
    expected = models.CharField(
        "Resultado Esperado",
        max_length=120
    )

    def __str__(self):
        return self.expected

    class Meta:
        verbose_name = "Resultado Esperado"
        verbose_name_plural = "Resultados Esperados"

class Componentes(models.Model):
    nome_componente = models.CharField(
        "Componente a ser testado", 
        blank=False, 
        max_length = 120
    )
    feature = models.ManyToManyField(
        Feature,
        verbose_name='Funcionalidade', 
        blank = True
    )
    qtd = models.CharField(
        max_length=50,
        verbose_name="Quantidade mínima de casos necessários",
        null=True
    )

    def __str__(self):
        return self.nome_componente

    class Meta:
        verbose_name = "Componente"
        verbose_name_plural = "Componentes"

class Case(models.Model):

    name = models.CharField(
        verbose_name="Nome",
        max_length=250
    )
    num_case = models.CharField(
        verbose_name='Número do caso',
        max_length = 20,
        blank=True,
        null = True,
        editable=False
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
    )
    component = models.ForeignKey(
        Componentes,
        on_delete=models.DO_NOTHING,
    )
    precondition = models.CharField(
        verbose_name="Pré-Condição",
        max_length = 250
    )
    inputs = models.CharField(
        verbose_name="Entradas",
        max_length = 250,
        default="Nenhuma",
        null=True,
        blank=True
    )
    action = models.CharField(
        verbose_name="Ação",
        max_length = 250
    )
    expected = models.CharField(
        verbose_name="Resultado Esperado",
        max_length = 250
    )
    postcondition = models.CharField(
        verbose_name="Pós-Condição",
        max_length = 250
    )
    date = models.DateTimeField(
        verbose_name="Data de Criação",
        default = timezone.localtime(timezone.now())
    )
    
    def __str__(self):
        return "Funcionalidade: "+str(self.feature.name)+" - Caso: " + str(self.num_case)

    class Meta:
        verbose_name = "Caso"
        verbose_name_plural = "Casos"

class Notification(models.Model):
    
    requester = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null = True
    )
    read = models.BooleanField(
        verbose_name="Lida",
        default = False
    )
    feature = models.ForeignKey(
        Feature,
        on_delete = models.DO_NOTHING,
        null = True,
        blank = True
    )
    pending = models.BooleanField(
        verbose_name="Pendente",
        default = True
    )

