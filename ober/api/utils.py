import json, re, types
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError

WATERFALL_IN = '__all'
waterfallre = re.compile(WATERFALL_IN + r'$')


class Glue():
  def __init__(self, request, queryset, extra_ordering=[], perform_q=True):
    self.filters, self.filtersWaterfall = filters_from_request(request=request)
    self.excludes, self.excludesWaterfall = filters_from_request(request=request, field_name='exclude')
    
    self.overlaps = overlaps_from_request(request=request)
    self.ordering = orderby_from_request(request=request)
    self.extra_ordering = extra_ordering
    self.queryset = queryset
    self.warnings = None

    if perform_q:
      self.search_query = search_from_request(request=request, klass=queryset.model)


    try:
      self.queryset = self.queryset.exclude(**self.excludes).filter(**self.filters)
      
      if perform_q and self.search_query:
        self.queryset = self.queryset.filter(self.search_query)

      if self.overlaps:
        self.queryset = self.queryset.filter(self.overlaps)
        

    except FieldError as e:
      self.warnings = {
        'filters': '%s' % e
      }
      pass
    except TypeError as e:
      pass
    # print self.warnings
    # apply filters progressively
    for fil in self.filtersWaterfall:
      # print fil
      try:
        self.queryset = self.queryset.filter(**fil)
      except FieldError as e:
        pass
      except TypeError as e:
        pass

    # @todo add rank annotation

    # print self.warnings, self.excludes

    if self.ordering is not None:
      #print self.ordering, '--', self.validated_ordering()
      self.queryset = self.queryset.order_by(*self.validated_ordering())

    #print self.queryset.query
  
  def get_hash(self, request):
    import hashlib
    m = hashlib.md5()
    m.update(json.dumps(request.query_params, ensure_ascii=False))
    return m.hexdigest()
    

  def get_verbose_info(self):
    _d = {
      # "orderby": self.validated_ordering(),
      "filters": filter(None, [ self.filters ] + self.filtersWaterfall),
      "exclude": filter(None, [ self.excludes ] + self.excludesWaterfall)
    }
    return _d

  
  def validated_ordering(self):
    _validated_ordering = []
    for field in self.ordering:
      _field = field.replace('-', '')
      _reverse = field.startswith('-')
      # placeolder for data relate ordering.
      if _field.startswith('data__'):
        # print 'data ordering '
        parts = _field.split('__')
        from django.db.models.expressions import RawSQL, OrderBy
        # last field startwith a numeric value (num_)?
        if parts[-1].startswith('num_'):
          _validated_ordering.append(OrderBy(RawSQL("cast(data->>%s as integer)", (parts[1],)), descending=_reverse), )
        else:
          # _validated_ordering.append(OrderBy(RawSQL("data->>%s", (parts[1],)), descending=True ))
          _validated_ordering.append(OrderBy(RawSQL("LOWER(%s.data->>%%s)" % (self.queryset.model._meta.db_table), (parts[1],)), descending=_reverse))

      elif _field not in self.extra_ordering:
        try:
          self.queryset.model._meta.get_field(_field)
        except Exception as e:
          self.warnings = {
            'ordering': '%s' % e
          }
        else:
          _validated_ordering.append('%s%s'%('-' if _reverse else '', _field))
      else:
       _validated_ordering.append('%s%s'%('-' if _reverse else '', _field))
    return _validated_ordering

# usage in viewsets.ModelViewSet methods, e;g. retrieve: 
# filters = filters_from_request(request=self.request) 
# qs = stories.objects.filter(**filters).order_by(*orderby)
def filters_from_request(request, field_name='filters'):
  filters = request.query_params.get(field_name, None)
  #print filters
  waterfall = []
  if filters is not None:
    try:
      filters = json.loads(filters)
      # print "filters,",filters
    except Exception, e:
      #print e
      filters = {}
  else:
    filters = {}
  # filter filters having _ prefixes (cascade stuffs)
  for k,v in filters.items():
    if k.endswith(WATERFALL_IN):
      if not isinstance(v, types.StringTypes):
        #print v
        for f in v:
          waterfall.append({
            waterfallre.sub('', k): f
          })
      else:
        waterfall.append({
          waterfallre.sub('', k): v
        })
      # get rifd of dirty filters
      filters.pop(k, None)

  return filters, waterfall



def search_from_request(request, klass):
  #print klass
  # understand if request has a search query
  search_query = request.query_params.get('q', None) 
  if search_query is None or len(search_query) < 2: #ignore less than two letters.
    return None
  else:
    try:
      q = klass.get_search_Q(query=search_query)
    except AttributeError:
      # method not found on the model specified
      return None
    else:
      return q

  


def overlaps_from_request(request, field_name='overlaps'):
  """
  Handle date range overlaps with django Q, since filters like `start_date__gt` and `end_date__lt` do not handle range verlaps

  Translate in dango Q
  
  case 1: left overlap (or outer) aka lov
       S |------------>| T 
    OS|----------->OT ..........--> OT?

  case 2: right overlap (or inner) aka rov
       S |------------>| T 
             OS|--->OT ..........--> OT?


  """
  overlaps = request.query_params.get(field_name, None)
  if not overlaps:
    return None
  start_date, end_date = zip(overlaps.split(','))

  lov  = Q(data__start_date__lte = start_date[0]) & Q(data__end_date__gte  = start_date[0])
  rov  = Q(data__start_date__gte = start_date[0]) & Q(data__start_date__lte = end_date[0])

  return lov | rov


# usage in viewsets.ModelViewSet methods, e;g. retrieve: 
# orderby = orderby_from_request(request=self.request) 
# qs = stories.objects.all().order_by(*orderby)
def orderby_from_request(request):
  orderby = request.query_params.get('orderby', None)
  return orderby.split(',') if orderby is not None else None

